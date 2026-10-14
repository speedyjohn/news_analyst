import logging
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Source

log = logging.getLogger(__name__)

SOURCES_FILE = Path(__file__).resolve().parents[2] / "sources.yaml"

_OPTION_KEYS = ("selectors", "language")
_COLUMNS = (
    "name", "country", "category_hint", "type", "url", "feed_url", "parser", "priority", "enabled",
)


def load_yaml(path: Path | None = None) -> list[dict]:
    path = path or SOURCES_FILE
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(data, list):
        raise ValueError(f"{path} должен содержать список источников")
    return data


_DEFAULTS = {
    "country": "KZ",
    "category_hint": None,
    "type": "rss",
    "feed_url": None,
    "parser": "rss",
    "priority": 3,
    "enabled": True,
}


def sync_from_yaml(session: Session, path: Path | None = None) -> int:
    changed = 0
    for entry in load_yaml(path):
        code = entry["code"]
        source = session.scalar(select(Source).where(Source.code == code))
        if source is None:
            source = Source(code=code)
            session.add(source)
            changed += 1
        for column in _COLUMNS:
            value = entry.get(column, _DEFAULTS.get(column))
            if getattr(source, column, None) != value:
                setattr(source, column, value)
                changed += 1
    session.flush()
    log.info("Синхронизация источников: %d изменений", changed)
    return changed


def parser_options(entry: dict) -> dict:
    return {key: entry[key] for key in _OPTION_KEYS if key in entry}


def list_sources(session: Session) -> list[Source]:
    return list(session.scalars(select(Source).order_by(Source.priority, Source.name)))
