from app.models import Source
from app.schemas.common import to_local


def source_row(source: Source) -> dict:
    return {
        "code": source.code,
        "name": source.name,
        "country": source.country,
        "type": source.type.upper(),
        "enabled": source.enabled,
        "last_success_at": to_local(source.last_success_at),
        "url": source.url,
        "host": source.url.split("//")[-1].split("/")[0].removeprefix("www."),
    }
