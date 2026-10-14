from app.core.errors import AppError
from app.parsers.base import BaseParser
from app.parsers.html.configurable import ConfigurableHtmlParser
from app.parsers.html.inform import InformParser
from app.parsers.html.primeminister import PrimeMinisterParser
from app.parsers.rss import RssParser

PARSERS: dict[str, type[BaseParser]] = {
    "rss": RssParser,
    "html": ConfigurableHtmlParser,
    "primeminister": PrimeMinisterParser,
    "inform": InformParser,
}


def build_parser(*, parser: str, code: str, url: str, feed_url: str | None, **options) -> BaseParser:
    parser_cls = PARSERS.get(parser)
    if parser_cls is None:
        raise AppError(
            f"Неизвестный парсер '{parser}' у источника {code}. Доступны: {', '.join(PARSERS)}",
            code="config_error",
            status=500,
        )
    return parser_cls(code=code, url=url, feed_url=feed_url, **options)
