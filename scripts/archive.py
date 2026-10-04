#!/usr/bin/env python3
"""archive.py — look up (and, if needed, create) Wayback Machine snapshots.

Companion to check_links.py. The site convention is to pair every "Original"
link with an "Archived" link of the form

    https://web.archive.org/web/<14-digit timestamp>/<url>

This tool answers three questions and does one bulk job:

  last  URL          most recent HTTP-200 snapshot
  until URL YYYYMMDD newest HTTP-200 snapshot no later than that date
                     (for articles pinned "as of" a publication date)
  save  URL          no snapshot? trigger Save Page Now, then print the
                     new link (polls the CDX index until it appears)
  links FILE...      for every Original link in one or more articles, print
                     the latest snapshot — with --save, also capture pages
                     that have none (the full Sources-section workflow)

Output is a ready-to-paste Archived URL (or link line with --paste).
Only the standard library is used; Wayback queries reuse the helpers and
politeness rules of check_links.py. Lookups retry with backoff, and the bulk
mode runs several lookups at once because archive.org's CDX endpoint can be
slow (seconds per query when throttled).

Exit status: 0 = all good, 1 = no snapshot found (last/until/save timed out
or a page has no capture), 3 = archive query failed (network / rate limit).
"""

import argparse
import random
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from check_links import (
    USER_AGENT,
    _cdx,
    archive_split,
    extract_links,
    fetch,
)

SAVE_ENDPOINT = "https://web.archive.org/save/"
SAVE_TIMEOUT = 360       # seconds to wait for a save to surface in the index
SAVE_POLL = 20
LOOKUP_ATTEMPTS = 3      # CDX is flaky when throttled: retry with backoff
LOOKUP_BACKOFF = (2, 4)
BULK_WORKERS = 4         # CDX answers slowly; overlap lookups
TIME_LIMIT = 30          # per-CDX-request timeout (s)
YEAR_PREFIX_RE = re.compile(r"^https?://web\.archive\.org/web/\d{4}/")

# ---------------------------------------------------------------------------
# lookups


def _is_archive_org(url):
    netloc = urllib.parse.urlparse(url).netloc.lower()
    return netloc == "archive.org" or netloc.endswith(".archive.org")


def last_snapshot(url, to=None):
    """Newest HTTP-200 snapshot timestamp, or (None, 'none'|'error'|'archived')."""
    if _is_archive_org(url):
        return None, "archived"  # already the archive; nothing to look up
    params = {
        "url": url,
        "output": "json",
        "fl": "timestamp",
        "filter": "statuscode:200",
        "sort": "reverse",
        "limit": "1",
    }
    if to:
        params["to"] = to + "235959" if len(to) == 8 else to
    for attempt in range(LOOKUP_ATTEMPTS):
        rows = _cdx(params, timeout=TIME_LIMIT)
        if rows is not None:
            return (rows[0], "ok") if rows else (None, "none")
        if attempt < LOOKUP_ATTEMPTS - 1:
            time.sleep(LOOKUP_BACKOFF[attempt])
    return None, "error"


def archived_link(ts, url):
    return f"https://web.archive.org/web/{ts}/{url}"


def print_result(ts, status, url, paste=False, err=sys.stderr):
    """Print one lookup outcome; returns the process exit code for it."""
    if status == "error":
        print(f"ERR   archive query failed: {url}", file=err)
        return 3
    if status == "archived":
        print(f"NOTE  {url} is itself an archive.org detail page; no Archived link needed")
        return 0
    if status == "none" or not ts:
        print(f"NONE  no HTTP-200 snapshot for {url}", file=err)
        return 1
    link = archived_link(ts, url)
    if paste:
        print(f"· [Archived]({link})")
    else:
        print(f"{ts}  {link}")
    return 0


# ---------------------------------------------------------------------------
# save


def save_page(url):
    """Trigger Save Page Now; return (job_started: bool, note: str)."""
    req = urllib.request.Request(
        SAVE_ENDPOINT + url, headers={"User-Agent": USER_AGENT}, method="GET"
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return False, ("Wayback save endpoint is rate-limited (HTTP 429); "
                           "wait a few minutes and retry")
        if e.code >= 400:
            return False, f"save endpoint returned HTTP {e.code}"
    except Exception as e:
        return False, f"save request failed: {type(e).__name__}: {e}"
    return True, ""


def cmd_save(url, wait=SAVE_TIMEOUT, poll=SAVE_POLL, paste=False):
    ts, status = last_snapshot(url)
    if status == "archived":
        print_result(None, "archived", url)
        return 0
    if status == "ok":
        print_result(ts, status, url, paste=paste)
        print("NOTE  a snapshot already exists; nothing was saved", file=sys.stderr)
        return 0
    started, note = save_page(url)
    if not started:
        print(note, file=sys.stderr)
        return 3
    deadline = time.time() + wait
    while time.time() < deadline:
        time.sleep(poll)
        ts, status = last_snapshot(url)
        if status == "ok":
            return print_result(ts, status, url, paste=paste)
    print(f"NONE  no snapshot surfaced within {wait}s; check back or save again",
          file=sys.stderr)
    return 1


# ---------------------------------------------------------------------------
# bulk: turn every Original link in an article into an Archived link

_jitter_guard = threading.Lock()


def _lookup_task(item):
    """One CDX lookup; jittered so parallel workers do not burst in step."""
    with _jitter_guard:
        time.sleep(random.uniform(0.05, 0.4))
    ts, status = last_snapshot(item["url"])
    return {**item, "ts": ts, "status": status, "rc": 0}


def cmd_links(files, save_missing=False, paste=False, workers=BULK_WORKERS):
    tasks = []
    exit_code = 0
    for path in files:
        if not Path(path).exists():
            print(f"not found: {path}", file=sys.stderr)
            exit_code = 3
            continue
        for n, url in extract_links(Path(path).read_text(encoding="utf-8")):
            if archive_split(url) or YEAR_PREFIX_RE.match(url) or _is_archive_org(url):
                continue  # already archived, or itself the archive
            tasks.append({"file": str(path), "line": n, "url": url})

    done = []
    if tasks:
        print(f"\nlooking up {len(tasks)} links...")
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_lookup_task, t) for t in tasks]
            for fut in as_completed(futures):
                item = fut.result()
                done.append(item)

    cur = None
    for r in sorted(done, key=lambda r: (r["file"], r["line"])):
        if r["file"] != cur:
            if cur is not None:
                print()
            cur = r["file"]
            print(f"== {r['file']} ==")
        print(f"  L{r['line']:>4}  {r['url']}")
        rc = print_result(r["ts"], r["status"], r["url"], paste=paste)
        exit_code = max(exit_code, rc)
        if r["status"] == "none" and save_missing:
            print("           -> saving...")
            exit_code = max(exit_code, cmd_save(r["url"], paste=paste))
    return exit_code


# ---------------------------------------------------------------------------
# CLI


def main():
    ap = argparse.ArgumentParser(
        description="Look up or create Wayback snapshots for URLs/articles.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_last = sub.add_parser("last", help="most recent HTTP-200 snapshot for a URL")
    p_last.add_argument("url")
    p_last.add_argument("--paste", action="store_true",
                        help="print the markdown '· [Archived](...)' fragment")

    p_until = sub.add_parser("until",
                             help="newest HTTP-200 snapshot no later than a date")
    p_until.add_argument("url")
    p_until.add_argument("date", help="YYYYMMDD (e.g. article publication date)")
    p_until.add_argument("--paste", action="store_true")

    p_save = sub.add_parser("save", help="capture a page now, then print its link")
    p_save.add_argument("url")
    p_save.add_argument("--wait", type=int, default=SAVE_TIMEOUT,
                        help=f"seconds to wait for capture (default {SAVE_TIMEOUT})")
    p_save.add_argument("--paste", action="store_true")

    p_links = sub.add_parser(
        "links", help="print an Archived link for every Original link in an article")
    p_links.add_argument("files", nargs="+")
    p_links.add_argument("--save", action="store_true",
                         help="capture pages that have no snapshot yet")
    p_links.add_argument("--paste", action="store_true")
    p_links.add_argument("--workers", type=int, default=BULK_WORKERS,
                         help="parallel lookups (default 4)")

    args = ap.parse_args()

    if args.cmd == "last":
        return print_result(*last_snapshot(args.url), args.url, paste=args.paste)
    if args.cmd == "until":
        if not re.fullmatch(r"\d{8}", args.date):
            ap.error("date must be YYYYMMDD")
        return print_result(*last_snapshot(args.url, to=args.date), args.url,
                            paste=args.paste)
    if args.cmd == "save":
        return cmd_save(args.url, wait=args.wait, paste=args.paste)
    if args.cmd == "links":
        return cmd_links(args.files, save_missing=args.save, paste=args.paste,
                         workers=args.workers)


if __name__ == "__main__":
    sys.exit(main())
