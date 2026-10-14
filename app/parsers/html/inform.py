from datetime import UTC, datetime

from app.parsers.base import RawArticle
from app.parsers.html.base_html import ALMATY, HtmlListParser, parse_ru_date


def _inform_datetime(value: str) -> datetime | None:
    if not value:
        return None
    # суффикс Z врёт, время на самом деле астанинское
    try:
        parsed = datetime.fromisoformat(value.replace("Z", ""))
    except ValueError:
        return None
    return parsed.replace(tzinfo=ALMATY).astimezone(UTC)


class InformParser(HtmlListParser):
    item_selector = "a.news-row, a.latest-news__item"
    title_selector = "h3.card-title"
    date_selector = "time.meta-date"
    body_selector = ".article__content"
    max_items = 40

    def parse_item(self, node):
        href = node.attributes.get("href", "")
        title_node = node.css_first(self.title_selector)
        date_node = node.css_first(self.date_selector)
        if not href or title_node is None or date_node is None:
            return None

        published = _inform_datetime(date_node.attributes.get("datetime", "")) or parse_ru_date(
            date_node.text()
        )
        if published is None:
            return None

        return RawArticle(
            title=title_node.text(strip=True),
            url=self.absolute(href),
            published_at=published,
            language="ru",
        )
