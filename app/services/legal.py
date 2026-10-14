import json
import logging
import re
from datetime import UTC, datetime, timedelta

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError, RateLimited, ValidationError
from app.llm.base import LLMProvider
from app.llm.prompts import load_prompt
from app.models import LegalAct, LegalArticle, LegalRequest, User
from app.services import textutil
from app.services.llm_gateway import ask_json

log = logging.getLogger(__name__)

MAX_INPUT_LEN = 2000
# больше не влезает по времени ответа
CONTEXT_ARTICLES = 12
ARTICLE_CHARS = 1200

NOT_ENOUGH = (
    "Не удалось подготовить обоснованное предложение: "
    "нет достаточной опоры в загруженной базе НПА."
)
MODEL_FAILED = "Модель не ответила. Запрос сохранён в истории, попробуйте отправить его ещё раз."
_FAILED_MARK = '"failed": true'

_QUERY_SCHEMA = {"problem_ru": "string", "keywords": ["string"]}

_SCHEMA = {
    "sufficient": "boolean",
    "title": "string",
    "problem": "string",
    "current_regulation": [
        {"act": "string", "article": "string", "point": "string|null", "quote": "string", "comment": "string"}
    ],
    "gap": "string",
    "proposal": "string",
    "rationale": "string",
}

_ARTICLE_MENTION = re.compile(r"(?:стать[а-яё]*|ст\.)\s*([0-9]+(?:-[0-9]+)?)", re.IGNORECASE)


def check_limits(session: Session, user: User) -> None:
    since = datetime.now(UTC) - timedelta(days=1)
    used = session.scalar(
        select(func.count(LegalRequest.id)).where(
            LegalRequest.user_id == user.id,
            LegalRequest.created_at >= since,
            or_(LegalRequest.output_text.is_(None), LegalRequest.output_text.not_like(f"%{_FAILED_MARK}%")),
        )
    )
    if used >= settings.legal_per_day:
        raise RateLimited(f"Не больше {settings.legal_per_day} запросов в юридический модуль в сутки.")


CANDIDATE_POOL = 300


def understand(session: Session, llm: LLMProvider, text: str) -> tuple[str, list[str]]:
    try:
        data = ask_json(
            session,
            llm,
            task="legal_query",
            system=load_prompt("legal_query"),
            user=text,
            schema=_QUERY_SCHEMA,
            max_tokens=500,
        )
    except Exception:
        log.exception("Не удалось разобрать юридический запрос, ищем по исходному тексту")
        return text, []

    problem_ru = str(data.get("problem_ru") or "").strip()
    raw = data.get("keywords")
    keywords = [str(k).strip() for k in raw if str(k).strip()] if isinstance(raw, list) else []
    return problem_ru or text, keywords[:12]


def _search_stems(problem: str, keywords: list[str]) -> list[str]:
    ordered = [w for k in keywords for w in textutil.significant_words(k)]
    ordered += sorted(textutil.significant_words(problem), key=len, reverse=True)
    stems: list[str] = []
    for word in ordered:
        if len(word) <= 4:
            continue
        base = textutil.stem(word)
        if base not in stems:
            stems.append(base)
    return stems[:16]


def find_articles(
    session: Session, problem: str, keywords: list[str] | None = None, limit: int = CONTEXT_ARTICLES
) -> list[LegalArticle]:
    keywords = keywords or []
    words = _search_stems(problem, keywords)
    if not words:
        return []

    weight = sum(
        [case((LegalArticle.title.ilike(f"%{w}%"), 3), else_=0) for w in words]
        + [case((LegalArticle.text.ilike(f"%{w}%"), 1), else_=0) for w in words]
    )
    conditions = [LegalArticle.text.ilike(f"%{w}%") for w in words]
    conditions += [LegalArticle.title.ilike(f"%{w}%") for w in words]

    candidates = session.scalars(
        select(LegalArticle).where(or_(*conditions)).order_by(weight.desc()).limit(CANDIDATE_POOL)
    ).all()

    query = " ".join([problem, *keywords])
    scored = [(_relevance(query, article), article) for article in candidates]
    return [a for score, a in sorted(scored, key=lambda p: -p[0]) if score > 0][:limit]


def _relevance(problem: str, article: LegalArticle) -> float:
    query = textutil.significant_stems(problem)
    if not query:
        return 0.0

    title_words = textutil.significant_stems(article.title or "")
    body_words = textutil.significant_stems(article.text)
    if not body_words and not title_words:
        return 0.0

    title_hits = len(query & title_words)
    body_hits = len(query & body_words)
    density = body_hits / max(len(body_words), 1) ** 0.5
    return title_hits * 2.0 + density * 10.0


def _context(articles: list[LegalArticle]) -> str:
    blocks = []
    for article in articles:
        blocks.append(
            f"Акт: {article.act.short_title or article.act.title}\n"
            f"Статья {article.number}. {article.title or ''}\n"
            f"{article.text[:ARTICLE_CHARS]}"
        )
    return "\n\n---\n\n".join(blocks)


def verify(session: Session, note: dict, allowed: list[LegalArticle]) -> tuple[bool, list[str]]:
    # модель выдумывает номера статей, сверяем с базой
    allowed_numbers = {a.number for a in allowed}
    by_number = {a.number: a for a in allowed}
    invalid: list[str] = []
    valid_refs = 0

    for item in note.get("current_regulation") or []:
        number = str(item.get("article") or "").strip()
        number = _ARTICLE_MENTION.sub(r"\1", number) if not number.isdigit() else number
        if number in allowed_numbers:
            valid_refs += 1
            item["article"] = number
            item["adilet_url"] = by_number[number].act.url
            item["act"] = by_number[number].act.short_title or by_number[number].act.title
        else:
            invalid.append(number or "(пусто)")

    for field in ("proposal", "rationale", "gap"):
        for mention in _ARTICLE_MENTION.findall(note.get(field) or ""):
            if mention not in allowed_numbers:
                invalid.append(mention)

    return (valid_refs > 0 and not invalid), invalid


def _generate(
    session: Session,
    llm: LLMProvider,
    problem: str,
    articles: list[LegalArticle],
    extra: str = "",
    problem_ru: str = "",
) -> dict:
    restated = (
        f"Та же проблема на русском юридическом языке:\n{problem_ru}\n\n"
        if problem_ru and problem_ru != problem
        else ""
    )
    return ask_json(
        session,
        llm,
        task="legal_suggestion",
        system=load_prompt("legal_suggestion"),
        user=(
            f"Проблема пользователя (как написал пользователь):\n{problem}\n\n"
            f"{restated}"
            f"Разрешённые номера статей — только эти: "
            f"{', '.join(sorted({a.number for a in articles}))}.\n"
            f"Любой другой номер делает ответ недействительным.\n\n"
            f"Доступные действующие нормы (ссылаться можно только на них):\n\n{_context(articles)}"
            f"{extra}"
        ),
        schema=_SCHEMA,
        max_tokens=3000,
    )


def suggest(session: Session, llm: LLMProvider, *, user: User, text: str) -> LegalRequest:
    text = (text or "").strip()
    if not text:
        raise ValidationError("Опишите проблему в регулировании")
    if len(text) > MAX_INPUT_LEN:
        raise ValidationError(f"Описание длиннее {MAX_INPUT_LEN} символов")

    check_limits(session, user)
    request = LegalRequest(user_id=user.id, input_text=text)
    session.add(request)
    session.flush()

    problem_ru, keywords = understand(session, llm, text)
    articles = find_articles(session, problem_ru, keywords)
    if not articles and problem_ru != text:
        articles = find_articles(session, text)
    if not articles:
        request.verified = False
        request.output_text = json.dumps({"error": NOT_ENOUGH}, ensure_ascii=False)
        return request

    try:
        note = _draft(session, llm, text, problem_ru, articles)
    except Exception:
        log.exception("Генерация записки упала, запрос %s сохранён со сбоем", request.id)
        request.verified = False
        request.output_text = json.dumps({"error": MODEL_FAILED, "failed": True}, ensure_ascii=False)
        return request

    if note is None:
        request.verified = False
        request.output_text = json.dumps({"error": NOT_ENOUGH}, ensure_ascii=False)
        return request

    request.verified = True
    request.output_text = json.dumps(note, ensure_ascii=False)
    return request


def _draft(
    session: Session, llm: LLMProvider, text: str, problem_ru: str, articles: list[LegalArticle]
) -> dict | None:
    note = _generate(session, llm, text, articles, problem_ru=problem_ru)
    ok, invalid = verify(session, note, articles)

    if not ok and invalid:
        log.warning("Невалидные ссылки на статьи: %s. Повтор.", invalid)
        note = _generate(
            session,
            llm,
            text,
            articles,
            extra="\n\n"
            + load_prompt("legal_retry").format(
                invalid=", ".join(invalid),
                allowed=", ".join(sorted({a.number for a in articles})),
            ),
            problem_ru=problem_ru,
        )
        ok, invalid = verify(session, note, articles)

    if not ok or not note.get("sufficient", True):
        return None
    return note


def requests_of(session: Session, user: User) -> list[LegalRequest]:
    return list(
        session.scalars(
            select(LegalRequest)
            .where(LegalRequest.user_id == user.id)
            .order_by(LegalRequest.created_at.desc())
        )
    )


def acts_loaded(session: Session) -> int:
    return session.scalar(select(func.count(LegalAct.id))) or 0


def require_corpus(session: Session) -> None:
    if acts_loaded(session) == 0:
        raise AppError(
            "База НПА не загружена. Запустите scripts/load_legal.py.",
            code="legal_corpus_empty",
            status=503,
        )
