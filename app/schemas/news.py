from app.models import News
from app.schemas.common import to_local


def source_brief(news: News) -> dict:
    return {
        "code": news.source.code,
        "name": news.source.name,
        "host": news.source.url.split("//")[-1].split("/")[0].removeprefix("www."),
    }


def news_card(news: News, counts: tuple[int, int] | None = None) -> dict:
    closed, total = counts or (0, 0)
    return {
        "id": news.id,
        "title": news.title,
        "summary": news.summary,
        "url": news.url,
        "published_at": to_local(news.published_at),
        "country": news.country,
        "category": news.category,
        "importance_score": news.importance_score,
        "source": source_brief(news),
        "questions": {"closed": closed, "total": total},
    }


def news_full(news: News) -> dict:
    data = news_card(news)
    data["full_text"] = news.full_text
    data["importance_reason"] = news.importance_reason
    data["language"] = news.language
    return data


def feed_response(payload: dict) -> dict:
    counts = payload["counts"]
    return {
        "items": [news_card(n, counts.get(n.id)) for n in payload["items"]],
        "total": payload["total"],
        "page": payload["page"],
        "page_size": payload["page_size"],
    }
