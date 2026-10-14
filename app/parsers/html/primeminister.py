from app.parsers.base import RawArticle
from app.parsers.html.base_html import HtmlListParser, parse_ru_date


class PrimeMinisterParser(HtmlListParser):
    item_selector = "div.blog__container a.article"
    title_selector = "h3.article__heading"
    date_selector = "span.article__date"
    body_selector = "div.articles__container"
    max_items = 30

    def parse_item(self, node):
        href = node.attributes.get("href", "")
        title_node = node.css_first(self.title_selector)
        date_node = node.css_first(self.date_selector)
        if not href or title_node is None or date_node is None:
            return None

        published = parse_ru_date(date_node.text())
        if published is None:
            return None

        return RawArticle(
            title=title_node.text(strip=True),
            url=self.absolute(href),
            published_at=published,
            language="ru",
        )
