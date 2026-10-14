import hashlib
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime

from selectolax.parser import HTMLParser

_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_SPACES = re.compile(r"\s+")

# иначе инлайн-скрипты попадают в текст новости
_JUNK_TAGS = ["script", "style", "noscript", "template", "iframe", "svg"]


def clean_tree(html: str) -> HTMLParser:
    tree = HTMLParser(html)
    tree.strip_tags(_JUNK_TAGS)
    return tree


def content_hash(title: str) -> str:
    normalized = _SPACES.sub("", _PUNCT.sub("", title.lower()))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@dataclass(slots=True)
class RawArticle:
    title: str
    url: str
    published_at: datetime
    full_text: str = ""
    language: str = "ru"
    extra: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.title = _SPACES.sub(" ", self.title).strip()
        # без зоны считаем UTC
        if self.published_at.tzinfo is None:
            self.published_at = self.published_at.replace(tzinfo=UTC)
        else:
            self.published_at = self.published_at.astimezone(UTC)

    @property
    def content_hash(self) -> str:
        return content_hash(self.title)


class BaseParser(ABC):
    def __init__(self, *, code: str, url: str, feed_url: str | None = None, **options):
        self.code = code
        self.url = url
        self.feed_url = feed_url
        self.options = options

    @abstractmethod
    def fetch(self, since: datetime) -> list[RawArticle]: ...

    def page_text(self, url: str) -> str:
        return ""
