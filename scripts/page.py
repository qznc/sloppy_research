#!/usr/bin/env python3
"""page.py — fetch a page's contents from hister's local index, given a URL.

The Sloppy workflow relies on hister's local web index, which keeps the raw
HTML of pages that were visited (or otherwise indexed), so content stays
available even when the live site is blocked or gone. This script is the
"URL in, readable text out" helper: it looks up the newest snapshot hister
has for a URL and dumps it as plain text.

How it works
------------
  1. Query `hister search <url>` (JSON, newest-first) — hister's full-text
     search does not index URLs reliably, so the first probe returns match
     results that may *not* contain the URL at all.
  2. Find the result whose normalized URL equals the requested one (strip
     scheme / www. / trailing slash / fragment). Because the URL itself is
     not always a good query, an exact hit may come from a search by title
     keywords instead (`--title`), or from a combined host+path keyword
     probe that runs automatically.
  3. Every other result is ignored: an unmatched top hit (a full-text match
     on some other page) is never dumped by accident; use `--all` to
     override.
  4. The stored `html` field is dumped to text with `lynx -dump -nolist`
     (the `text` field in hister comes back empty, so HTML + lynx it is).

If hister has no snapshot of the URL the script says so and exits 1. It does
not fetch the network — that is the point. To get a page *into* the index,
open it in a browser with hister's companion running, or `hister index <url>`.

Only the standard library is used, plus `lynx` for the text dump.
"""

import argparse
import json
import re
import subprocess
import sys
from urllib.parse import urlparse

HISTER = "hister"
LYNX = "lynx"
PROBE_LIMIT = 10      # results pulled per hister probe
# The URL itself is a lousy hister query (it ranks barely above unrelated
# full-text hits), but combining the most distinctive host and path words
# into one query (e.g. "simonwillison slop") reliably surfaces the page.
# The second probe uses these tokens; an exact URL match is still required,
# so a wrong page is never misattributed.
QUERY_TOKENS = 4      # max distinctive tokens per probe query
TLD_WORDS = {"com", "net", "org", "edu", "gov", "io", "co", "uk", "de",
             "info", "html", "www"}

_TRAILING_COMMA_RE = re.compile(r",\s*]")


def norm_url(url: str) -> str:
    """Normalize a URL for exact matching (host+path+query, no noise)."""
    p = urlparse(url)
    host = (p.hostname or "").lower().removeprefix("www.")
    path = p.path.rstrip("/")
    query = "?" + p.query if p.query else ""
    return f"{host}{path}{query}"


def hister_json(query: str, limit: int) -> list[dict]:
    """Run a hister search and parse its JSON output (trailing comma quirk)."""
    cmd = [
        HISTER, "search", query,
        "-f", "json",
        "-F", "url,title,html",
        "-L", str(limit),
        "-s", "date",          # newest snapshot first, as in the manual workflow
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"hister search failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    raw = proc.stdout.strip()
    if not raw:
        return []
    return json.loads(_TRAILING_COMMA_RE.sub("]", raw))


def find_page(url: str, results: list[dict]):
    want = norm_url(url)
    for r in results:
        if norm_url(r.get("url", "")) == want:
            return r
    return None


def distinctive_query(url: str) -> str | None:
    """Build an AND-ish probe query from the URL's most distinctive words.

    Hister tokenizes host + title + body, so words taken from the host and
    the longest path segments make a good probe: e.g.
    https://simonwillison.net/2024/May/8/slop/ -> "simonwillison slop".
    """
    p = urlparse(url)
    host = (p.hostname or "").lower().removeprefix("www.")
    words = [
        w for w in re.split(r"[^a-z0-9]+", host)
        if w and w not in TLD_WORDS
    ]
    segments = [
        s for s in re.split(r"[^A-Za-z0-9._-]+", p.path)
        if len(s) > 2 and s.lower() not in TLD_WORDS
    ]
    # Longest path segments are the most distinctive; longer-scored first.
    segments.sort(key=len, reverse=True)
    tokens = (words[:1] + segments)[:QUERY_TOKENS]
    if not tokens:
        return None
    return " ".join(dict.fromkeys(t for t in tokens))  # dedupe, keep order


def lookup(url: str | None, title: str | None, all_results: bool):
    queries = []
    if title:
        queries.append(title)                    # explicit title/search phrase
        if url:
            queries.append(url)
    else:
        queries.append(url or "")               # whole URL first
        probe = distinctive_query(url or "")
        if probe:
            queries.append(probe)

    seen: dict[str, list[dict]] = {}
    for q in queries:
        results = hister_json(q, PROBE_LIMIT)
        if results:
            if not url:
                # Title-only lookup: nothing to verify against; top hit is it.
                return results[0], results
            page = find_page(url, results)
            if page is not None:
                return page, results
            if not all_results:
                seen[q] = results

    # Nothing matched the URL exactly.
    if all_results and queries:
        # The user said "gimme the first hit" and no exact match exists;
        # fall back to the first probe's top result.
        first = hister_json(queries[0], PROBE_LIMIT)
        if first:
            return first[0], first
    raise PageNotFound(url or "", seen)


class PageNotFound(Exception):
    def __init__(self, url: str, probes: dict[str, list[dict]]):
        self.url = url
        self.probes = probes
        super().__init__(f"no hister snapshot for {url}")


def dump_html(html: str) -> None:
    proc = subprocess.run(
        [LYNX, "-dump", "-nolist", "-stdin"],
        input=html, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"lynx failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    sys.stdout.write(proc.stdout)


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="page.py",
        description="Fetch a page's contents from hister's local index by URL.",
    )
    ap.add_argument("url", nargs="?", help="URL to look up in hister (or - omit with --title)")
    ap.add_argument("--title", metavar="TITLE",
                    help="search hister by these words instead of the URL")
    ap.add_argument("--html", action="store_true",
                    help="print the stored HTML instead of lynx text")
    ap.add_argument("--all", action="store_true",
                    help="dump the top match even if its URL does not match")
    ap.add_argument("--json", action="store_true",
                    help="print the matched snapshot as JSON (url/title/html)")
    args = ap.parse_args()
    if not args.url and not args.title:
        ap.error("a URL or --title is required")

    try:
        page, _results = lookup(args.url, args.title, args.all)
    except PageNotFound as e:
        sys.stderr.write(f"page.py: no snapshot of {e.url} in hister's index.\n")
        if e.probes:
            found = {
                norm_url(r["url"])
                for hits in e.probes.values()
                for r in hits if r.get("url")
            }
            if found:
                sys.stderr.write("closest hits (URLs differ):\n")
                for u in sorted(found):
                    sys.stderr.write(f"  {u}\n")
        sys.stderr.write(
            "Open the page in a browser (hister companion running) or run\n"
            f"  {HISTER} index {e.url}\n"
            "then retry.\n"
        )
        return 1

    if args.json:
        json.dump(page, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
    elif args.html:
        sys.stdout.write(page.get("html", "") or "")
    else:
        dump_html(page.get("html", "") or "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
