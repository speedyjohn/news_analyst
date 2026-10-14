import logging
import ssl
from functools import lru_cache
from pathlib import Path

import certifi
import httpx

from app.core.config import settings

log = logging.getLogger(__name__)

# на дефолтный UA часть госсайтов отвечает 403
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NewsAnalyticsBot/1.0; +https://example.kz/bot)",
    "Accept-Language": "ru,ru-RU;q=0.9",
}

CERTS_DIR = Path(__file__).parent / "certs"


@lru_cache
def ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context(cafile=certifi.where())
    # госсайты не присылают промежуточный сертификат, в докере без него не работает
    for pem in sorted(CERTS_DIR.glob("*.pem")):
        context.load_verify_locations(cafile=str(pem))
        log.debug("Добавлен промежуточный сертификат %s", pem.name)
    return context


def fetch(url: str, *, timeout: int | None = None) -> str:
    verify = ssl_context() if settings.http_verify_ssl else False
    with httpx.Client(
        timeout=timeout or settings.http_timeout,
        follow_redirects=True,
        headers=_HEADERS,
        verify=verify,
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        log.info("GET %s -> %s (%d bytes)", url, response.status_code, len(response.content))
        # charset не указан - httpx гадает и часто ошибается
        if response.encoding is None or response.encoding.lower() == "iso-8859-1":
            return response.content.decode("utf-8", errors="replace")
        return response.text
