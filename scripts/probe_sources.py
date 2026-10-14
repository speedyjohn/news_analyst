# python scripts/probe_sources.py [коды...] [--url URL]
import argparse
import sys
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import feedparser  # noqa: E402
from selectolax.parser import HTMLParser  # noqa: E402

from app.core.http import fetch  # noqa: E402
from app.services.sources import load_yaml  # noqa: E402

COMMON_PATHS = ("/rss", "/rss.xml", "/feed", "/feed.xml", "/ru/rss", "/ru/feed", "/rss/news")


def discover(url: str) -> list[str]:
    found: list[str] = []
    try:
        tree = HTMLParser(fetch(url, timeout=15))
        for node in tree.css('link[type="application/rss+xml"], link[type="application/atom+xml"]'):
            href = node.attributes.get("href")
            if href:
                found.append(urljoin(url, href))
    except Exception as exc:  # noqa: BLE001
        print(f"    страница не открылась: {type(exc).__name__}: {exc}")

    root = "/".join(url.split("/")[:3])
    found.extend(urljoin(root, path) for path in COMMON_PATHS)
    return list(dict.fromkeys(found))


def check_feed(url: str) -> tuple[bool, int, str]:
    try:
        feed = feedparser.parse(fetch(url, timeout=15))
    except Exception as exc:  # noqa: BLE001
        return False, 0, type(exc).__name__
    if not feed.entries:
        return False, 0, "не разобрался" if feed.bozo else "пустой фид"
    return True, len(feed.entries), feed.feed.get("title", "")[:40]


def probe(code: str, url: str, feed_url: str | None = None) -> None:
    candidates = ([feed_url] if feed_url else []) + discover(url)
    for candidate in candidates:
        ok, count, note = check_feed(candidate)
        if ok:
            print(f"{code:<16}{'есть':<6}{count:<9}{candidate}   {note}")
            return
    print(f"{code:<16}{'нет':<6}{'—':<9}требует html-адаптера ({url})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Проверка наличия RSS у источников")
    parser.add_argument("codes", nargs="*", help="коды источников из sources.yaml")
    parser.add_argument("--url", help="проверить произвольный адрес, минуя sources.yaml")
    args = parser.parse_args()

    print(f"{'КОД':<16}{'RSS':<6}{'ЗАПИСЕЙ':<9}АДРЕС")
    print("-" * 96)

    if args.url:
        probe("(--url)", args.url)
        return

    entries = load_yaml()
    if args.codes:
        entries = [e for e in entries if e["code"] in args.codes]
    for entry in entries:
        probe(entry["code"], entry["url"], entry.get("feed_url"))


if __name__ == "__main__":
    main()
