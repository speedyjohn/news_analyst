from app.parsers.html.base_html import HtmlListParser


class ConfigurableHtmlParser(HtmlListParser):
    def __init__(self, **kw):
        super().__init__(**kw)
        selectors = self.options.get("selectors") or {}
        self.item_selector = selectors.get("item", "article")
        self.title_selector = selectors.get("title", "a")
        self.link_selector = selectors.get("link", "a")
        self.date_selector = selectors.get("date", "")
        self.body_selector = selectors.get("body", "")
        self.max_items = int(selectors.get("max_items", 25))
