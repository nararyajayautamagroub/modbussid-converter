#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.scraper import crawl_site, scrape_page
from shared.version import APP_VERSION


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Game Mod Asset Lab v4.1 scraper"
    )
    parser.add_argument("url", help="URL HTTP/HTTPS publik")
    parser.add_argument(
        "--crawl",
        action="store_true",
        help="Crawl host yang sama, bukan hanya satu halaman",
    )
    parser.add_argument("--max-pages", type=int, default=5)
    parser.add_argument("--max-links", type=int, default=50)
    parser.add_argument("--max-bytes", type=int, default=5 * 1024 * 1024)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--output", type=Path)

    args = parser.parse_args()

    if args.crawl:
        result = crawl_site(
            args.url,
            max_pages=args.max_pages,
            max_links_per_page=args.max_links,
            timeout=args.timeout,
        )
    else:
        result = scrape_page(
            args.url,
            max_bytes=args.max_bytes,
            max_links=args.max_links,
            timeout=args.timeout,
        )

    result["tool_version"] = APP_VERSION
    payload = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(args.output)
    else:
        print(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
