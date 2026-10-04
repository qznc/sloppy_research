#!/usr/bin/env python3
"""check_links.py — verify external links in Sloppy Research articles.

Checks every http(s) link in one or more src/*.md files:

  * "Original" links are fetched directly (GET, browser user-agent,
    redirects followed) and classified.
  * web.archive.org "Archived" links are fetched directly too. The site's
    convention is the year-prefix form  https://web.archive.org/web/YYYY/<url> ,
    which returns 404 if no snapshot exists in that year, so a direct fetch
    tells us whether the link exactly as published actually resolves. When it
    does not, the Wayback availability API is queried for the closest real
    snapshot, so the author can paste a correct timestamp.

Exit status: 0 = no dead links, 2 = at least one confirmed dead (404/410) link.
Rate-limiting, bot-blocking and network failures are "unverified", not errors:
by default they never affect the exit code (use --fail-warnings to also fail on
those). They are printed so a human can double-check blocked pages in a browser.

Only standard library is used, so it runs under any Python 3 without
installing dependencies. It is a polite checker: low concurrency, timeouts,
and a few retries on transient answers. It does not check robots.txt; it is
meant to be run by a human on a handful of articles, not as a bulk crawler.
"""

import argparse
import json
import re
import socket
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT, "Accept": "*/*"}

LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(\s*(https?://[^)\s]+)\s*\)")
TIMEOUT = 30
RETRIES = 2
WORKERS = 6
# Wayback throttles parallel requests aggressively, so serialise the two
# archive.org hosts; other hosts may run 2 at a time.
HOST_LIMIT = {"archive.org": 1, "web.archive.org": 1}
HOST_LOCK = {}  # host -> (semaphore)
_host_locks_guard = threading.Lock()


def host_semaphore(host):
    with _host_locks_guard:
        if host not in HOST_LOCK:
            HOST_LOCK[host] = threading.Semaphore(HOST_LIMIT.get(host, 2))
        return HOST_LOCK[host]
# Wayback timestamps: full = 14 digits, or shortened like "2026".
ARCHIVE_PREFIX_RE = re.compile(r"^https?://web\.archive\.org/web/([0-9a-zA-Z_*\-/]*?)/(https?://.*)$")

# Status classification helpers.
class Code:
    OK = "ok"            # 2xx or 3xx after redirects
    DEAD = "dead"        # 404 / 410 — link is broken
    BLOCKED = "blocked"  # 401/402/403/405 — likely anti-bot, may be fine for a human
    TRANSIENT = "transient"  # 429 or 5xx — retry later
    ERROR = "error"      # network / TLS / DNS / timeout


def classify(code, final=None, reason=None):
    if code is None:
        return Code.ERROR, reason or "no response"
    if 200 <= code < 400:
        return Code.OK, f"HTTP {code}"
    if code in (404, 410):
        return Code.DEAD, f"HTTP {code}"
    if code in (401, 402, 403, 405):
        return Code.BLOCKED, f"HTTP {code}"
    if code in (429, 500, 502, 503, 504):
        return Code.TRANSIENT, f"HTTP {code}"
    return Code.TRANSIENT, f"HTTP {code}"


def fetch(url, timeout=TIMEOUT, retries=RETRIES):
    """GET a URL, follow redirects, return (kind, detail, final_url)."""
    final = None
    last_err = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers=HEADERS, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                final = resp.geturl()
                kind, detail = classify(resp.getcode(), final)
                return kind, detail, final
        except urllib.error.HTTPError as e:
            kind, detail = classify(e.code)
            if kind == Code.TRANSIENT and attempt < retries:
                last_err = detail
                time.sleep(2 * (attempt + 1))
                continue
            return kind, detail, e.geturl() or final
        except (urllib.error.URLError, TimeoutError, socket.timeout,
                ConnectionError, ssl.SSLError, OSError) as e:
            reason = (getattr(e, "reason", None) or e)
            if attempt < retries:
                last_err = reason
                time.sleep(2 * (attempt + 1))
                continue
            return Code.ERROR, f"{type(reason).__name__}: {reason}", final
        except ValueError as e:
            return Code.ERROR, f"bad URL: {e}", final
    return Code.ERROR, f"gave up after retries: {last_err}", final


CDX = "https://web.archive.org/cdx/search/cdx"


def _cdx(params, timeout=TIMEOUT):
    """One CDX query. Returns list of timestamp rows, [] for none, None on error."""
    url = CDX + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers=HEADERS, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.getcode() != 200:
                return None
            rows = json.loads(resp.read().decode("utf-8", "replace"))
        # rows = [[timestamp, ...], ...]; CDX JSON may include a header row
        # (e.g. ["timestamp"]) as the first element, which must be ignored.
        ts = [r[0] for r in rows if r and str(r[0]).isdigit()]
        return ts
    except Exception:
        return None


def cdx_closest(url, timeout=TIMEOUT):
    """Find the closest usable (HTTP 200) snapshot for a URL.

    Returns (ts, era) where era is '2026' | 'earlier' | 'later', or
    (None, 'none') if the page was never captured, or (None, 'error')
    if the archive could not be queried.
    """
    last = _cdx({"url": url, "output": "json", "fl": "timestamp",
                 "filter": "statuscode:200", "to": "20261231235959",
                 "limit": "1", "sort": "reverse"}, timeout)
    if last is None:
        return None, "error"
    if last:
        ts = last[0]
        return ts, ("2026" if ts.startswith("2026") else "earlier")
    first = _cdx({"url": url, "output": "json", "fl": "timestamp",
                  "filter": "statuscode:200", "from": "20270101000000",
                  "limit": "1"}, timeout)
    if first is None:
        return None, "error"
    if first:
        return first[0], "later"
    return None, "none"


def extract_links(text):
    """Return list of (line_no, url) for every external markdown link."""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        for m in LINK_RE.finditer(line):
            out.append((n, m.group(1)))
    return out


def archive_split(url):
    """If url is an Archive.org link, return (prefix_ts, original); else None."""
    m = ARCHIVE_PREFIX_RE.match(url.strip())
    if m:
        return m.group(1), m.group(2)
    return None


def _job_archived(n, url, arch):
    """Check an archive.org 'Archived' link; suggest a working timestamp if broken."""
    st, detail, final = fetch(url)
    if st == Code.OK:
        return {"status": st, "detail": detail, "note": "(snapshot present)"}
    original = arch[1]
    ts, era = cdx_closest(original)
    if era == "error":
        note = f"(archive query failed after direct fetch {detail})"
    elif ts and ts.startswith("2026"):
        note = (f"2026 snapshot exists ({ts}) — direct fetch was {detail}; "
                f"suggest: https://web.archive.org/web/{ts}/{original}")
    elif ts:
        note = (f"no 2026 snapshot; nearest is {ts} ({era}) — "
                f"update Archived link to https://web.archive.org/web/{ts}/{original}")
    else:
        note = "no snapshot found at all — consider saving the page"
    return {"status": st, "detail": detail, "note": note}


def _job_locked(file_path, n, url):
    arch = archive_split(url)
    if arch:
        r = _job_archived(n, url, arch)
        return {"file": file_path, "line": n, "kind": "archived", "url": url,
                "final": None, **r}
    st, detail, final = fetch(url)
    return {"file": file_path, "line": n, "kind": "original", "url": url,
            "status": st, "detail": detail, "note": "", "final": final}


def job(file_path, entry):
    """Run one link check under a per-host throttle."""
    n, url = entry
    host = urllib.parse.urlparse(url).netloc.lower()
    with host_semaphore(host):
        try:
            return _job_locked(file_path, n, url)
        finally:
            # Wayback throttles aggressively even at low concurrency; leave
            # a short gap before the next request to the same archive hosts.
            if host in HOST_LIMIT:
                time.sleep(0.8)


def main():
    ap = argparse.ArgumentParser(description="Verify links in Sloppy Research articles.")
    ap.add_argument("files", nargs="*", help="markdown files to check")
    ap.add_argument("--all", action="store_true", help="check every src/*.md")
    ap.add_argument("--workers", type=int, default=WORKERS, help="concurrent requests")
    ap.add_argument("--timeout", type=int, default=TIMEOUT, help="per-request timeout (s)")
    ap.add_argument("--retries", type=int, default=RETRIES, help="retries per URL")
    ap.add_argument("--quiet", action="store_true", help="print only problems")
    ap.add_argument("--fail-warnings", action="store_true",
                    help="exit 1 also when links could not be verified "
                         "(rate-limited/bot-blocked/network)")
    args = ap.parse_args()

    if args.all:
        files = sorted(Path("src").rglob("*.md"))
    elif args.files:
        files = [Path(f) for f in args.files]
    else:
        ap.error("give at least one markdown file, or --all")

    jobs = []
    for path in files:
        if not path.exists():
            ap.error(f"not found: {path}")
        for n, url in extract_links(path.read_text(encoding="utf-8")):
            jobs.append((str(path), (n, url)))

    if not jobs:
        print("no external links found")
        return 0

    counts = {"ok": 0, "dead": 0, "unverified": 0}
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for res in pool.map(lambda e: job(e[0], e[1]), jobs):
            group = "ok" if res["status"] == Code.OK else (
                "dead" if res["status"] == Code.DEAD else "unverified")
            counts[group] += 1
            results.append(res)

    cur = None
    for r in sorted(results, key=lambda r: (r["file"], r["line"])):
        if r["file"] != cur:
            if cur is not None:
                sys.stderr.write("\n")
            cur = r["file"]
            print(f"\n== {r['file']} ==")
        flag = {
            Code.OK: "ok      ",
            Code.DEAD: "DEAD    ",
            Code.BLOCKED: "unverif.",
            Code.TRANSIENT: "unverif.",
            Code.ERROR: "unverif.",
        }[r["status"]]
        line = f"  L{r['line']:>4}  [{flag}] {r['detail']:<12} {r['url']}"
        if r["note"]:
            line += f"\n          -> {r['note']}"
        if r["status"] == Code.OK and args.quiet:
            continue
        print(line)

    sys.stderr.write("\n")
    sys.stderr.write(
        f"{len(jobs)} links: {counts['ok']} ok, {counts['dead']} dead, "
        f"{counts['unverified']} unverified "
        "(rate-limited / bot-blocked / network)\n"
    )

    if counts["dead"]:
        return 2
    if args.fail_warnings and counts["unverified"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
