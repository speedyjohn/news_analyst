import logging
from datetime import UTC, datetime
from urllib.parse import urljoin

import feedparser

from app.core.http import fetch as http_fetch
from app.parsers.base import BaseParser, RawArticle, clean_tree

log = logging.getLogger(__name__)

MIN_BODY_LEN = 400


def _clean_html(raw: str) -> str:
    if not raw:
        return ""
    return clean_tree(raw).text(separator="\n", strip=True)


def _parsed_datetime(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        value = getattr(entry, key, None)
        if value:
            return datetime(*value[:6], tzinfo=UTC)
    return None


class RssParser(BaseParser):
    def fetch(self, since: datetime) -> list[RawArticle]:
        feed_url = self.feed_url or self.url
        feed = feedparser.parse(http_fetch(feed_url))
        if feed.bozo and not feed.entries:
            raise ValueError(f"Невалидный фид {feed_url}: {feed.bozo_exception}")

        articles: list[RawArticle] = []
        for entry in feed.entries:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            published = _parsed_datetime(entry)
            if not title or not link or published is None:
                log.debug("%s: пропускаю запись без заголовка/ссылки/даты", self.code)
                continue

            body = ""
            if getattr(entry, "content", None):
                body = _clean_html(entry.content[0].value)
            if not body:
                body = _clean_html(getattr(entry, "summary", ""))

            article = RawArticle(
                title=title,
                url=urljoin(self.url, link),
                published_at=published,
                full_text=body,
                language=self.options.get("language", "ru"),
            )
            if article.published_at >= since:
                articles.append(article)

        body_selector = (self.options.get("selectors") or {}).get("body")
        if body_selector:
            for article in articles:
                if len(article.full_text) < MIN_BODY_LEN:
                    article.full_text = self._page_text(article.url, body_selector) or article.full_text
        return articles

    def _page_text(self, url: str, selector: str) -> str:
        try:
            nodes = clean_tree(http_fetch(url)).css(selector)
        except Exception:  # noqa: BLE001
            log.warning("%s: не удалось забрать текст %s", self.code, url)
            return ""
        texts = [node.text(separator="\n", strip=True) for node in nodes]
        return max(texts, key=len) if texts else ""

    def page_text(self, url: str) -> str:
        selector = (self.options.get("selectors") or {}).get("body")
        return self._page_text(url, selector) if selector else ""
