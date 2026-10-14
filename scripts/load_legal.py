# python scripts/load_legal.py [код]
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from selectolax.parser import HTMLParser  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.core.db import session_scope  # noqa: E402
from app.core.http import fetch  # noqa: E402
from app.models import LegalAct, LegalArticle  # noqa: E402

ACTS = [
    {
        "code": "koap",
        "short": "КоАП РК",
        "title": "Кодекс Республики Казахстан об административных правонарушениях",
        "url": "https://adilet.zan.kz/rus/docs/K1400000235",
    },
    {
        "code": "business",
        "short": "Предпринимательский кодекс РК",
        "title": "Предпринимательский кодекс Республики Казахстан",
        "url": "https://adilet.zan.kz/rus/docs/K1500000375",
    },
    {
        "code": "labor",
        "short": "Трудовой кодекс РК",
        "title": "Трудовой кодекс Республики Казахстан",
        "url": "https://adilet.zan.kz/rus/docs/K1500000414",
    },
    {
        "code": "civil",
        "short": "ГК РК (Общая часть)",
        "title": "Гражданский кодекс Республики Казахстан (Общая часть)",
        "url": "https://adilet.zan.kz/rus/docs/K940001000_",
    },
    {
        "code": "tax",
        "short": "НК РК",
        "title": "Кодекс Республики Казахстан «О налогах и других обязательных платежах в бюджет»",
        "url": "https://adilet.zan.kz/rus/docs/K1700000120",
    },
]

ARTICLE_HEAD = re.compile(r"^\s*Статья\s+([0-9]+(?:-[0-9]+)?)\.?\s*(.*)$", re.MULTILINE)


def split_articles(text: str) -> list[tuple[str, str, str]]:
    matches = list(ARTICLE_HEAD.finditer(text))
    result = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        number, title = match.group(1), match.group(2).strip()
        body = text[match.end() : end].strip()
        if body:
            result.append((number, title, body))
    return result


def load_act(spec: dict) -> int:
    print(f"Загружаю {spec['short']} ...")
    try:
        html = fetch(spec["url"], timeout=180)
    except Exception as exc:  # noqa: BLE001
        print(f"  не скачался: {type(exc).__name__}: {str(exc)[:120]}")
        return 0

    node = HTMLParser(html).css_first("#dc, .document, body")
    text = node.text(separator="\n", strip=True) if node else ""
    articles = split_articles(text)
    if not articles:
        print(f"  не нашёл ни одной статьи — разметка Adilet изменилась, проверьте {spec['url']}")
        return 0

    with session_scope() as session:
        act = session.scalar(select(LegalAct).where(LegalAct.adilet_code == spec["code"]))
        if act is None:
            act = LegalAct(adilet_code=spec["code"])
            session.add(act)
        act.title = spec["title"]
        act.short_title = spec["short"]
        act.url = spec["url"]
        session.flush()

        session.query(LegalArticle).filter(LegalArticle.act_id == act.id).delete()
        for number, title, body in articles:
            session.add(
                LegalArticle(act_id=act.id, number=number, title=title[:700] or None, text=body)
            )

    print(f"  сохранено статей: {len(articles)}")
    return len(articles)


def main(codes: list[str]) -> None:
    specs = [a for a in ACTS if not codes or a["code"] in codes]
    total = sum(load_act(spec) for spec in specs)
    print(f"\nИтого статей: {total}")


if __name__ == "__main__":
    main(sys.argv[1:])
