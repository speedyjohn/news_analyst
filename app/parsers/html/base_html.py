from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from selectolax.parser import HTMLParser

from app.core.http import fetch as http_fetch
from app.parsers.base import BaseParser, RawArticle, clean_tree

ALMATY = ZoneInfo("Asia/Almaty")

MONTHS_RU = {
    "январ": 1, "феврал": 2, "март": 3, "апрел": 4, "ма": 5, "июн": 6,
    "июл": 7, "август": 8, "сентябр": 9, "октябр": 10, "ноябр": 11, "декабр": 12,
}


def _month(token: str) -> int | None:
    token = token.strip().lower().rstrip(",.")
    for stem, number in MONTHS_RU.items():
        if token.startswith(stem):
            return number
    return None


def parse_ru_date(text: str, *, tz: ZoneInfo = ALMATY) -> datetime | None:
    cleaned = " ".join((text or "").split()).replace(",", " ")
    tokens = cleaned.split()

    hour = minute = 0
    for token in tokens:
        if ":" in token:
            parts = token.split(":")
            if parts[0].isdigit() and parts[1][:2].isdigit():
                hour, minute = int(parts[0]), int(parts[1][:2])
                break

    for index, token in enumerate(tokens):
        month = _month(token)
        if month is None or index == 0:
            continue
        try:
            day = int(tokens[index - 1])
        except ValueError:
            continue
        year = datetime.now(tz).year
        for candidate in tokens[index + 1 : index + 3]:
            if candidate.isdigit() and len(candidate) == 4:
                year = int(candidate)
                break
        try:
            local = datetime(year, month, day, hour, minute, tzinfo=tz)
        except ValueError:
            continue
        return local.astimezone(UTC)

    for token in tokens:
        for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                local = datetime.strptime(token, fmt).replace(hour=hour, minute=minute, tzinfo=tz)
            except ValueError:
                continue
            return local.astimezone(UTC)
    return None


def parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=ALMATY).astimezone(UTC)


class HtmlListParser(BaseParser):
    item_selector = "article"
    title_selector = "a"
    link_selector = "a"
    date_selector = ""
    body_selector = ""
    max_items = 25

    def fetch(self, since: datetime) -> list[RawArticle]:
        tree = HTMLParser(http_fetch(self.url))
        nodes = tree.css(self.item_selector)
        if not nodes:
            raise ValueError(f"{self.code}: селектор '{self.item_selector}' ничего не нашёл")

        articles: list[RawArticle] = []
        for node in nodes[: self.max_items]:
            article = self.parse_item(node)
            if article is None:
                continue
            if article.published_at < since:
                continue
            articles.append(article)

        for article in articles:
            article.full_text = self.body(article.url)
        return articles

    def parse_item(self, node) -> RawArticle | None:
        title_node = node.css_first(self.title_selector) if self.title_selector else node
        link_node = node.css_first(self.link_selector) if self.link_selector else node
        if title_node is None or link_node is None:
            return None
        href = link_node.attributes.get("href", "")
        title = title_node.text(strip=True)
        if not href or not title:
            return None

        published = None
        if self.date_selector:
            date_node = node.css_first(self.date_selector)
            if date_node is not None:
                published = parse_iso(date_node.attributes.get("datetime", "")) or parse_ru_date(
                    date_node.text()
                )
        if published is None:
            published = datetime.now(UTC)

        return RawArticle(
            title=title,
            url=self.absolute(href),
            published_at=published,
            language=self.options.get("language", "ru"),
        )

    def absolute(self, href: str) -> str:
        from urllib.parse import urljoin

        return urljoin(self.url, href)

    def body(self, url: str) -> str:
        if not self.body_selector:
            return ""
        try:
            nodes = clean_tree(http_fetch(url)).css(self.body_selector)
        except Exception:  # noqa: BLE001
            return ""
        texts = [node.text(separator="\n", strip=True) for node in nodes]
        # контейнер с тем же классом бывает несколько раз, берём самый длинный
        return max(texts, key=len) if texts else ""

    def page_text(self, url: str) -> str:
        return self.body(url)


def default_since(days: int = 1) -> datetime:
    return datetime.now(UTC) - timedelta(days=days)
