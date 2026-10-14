import re

# казахские буквы нужны, иначе «салық» не ищется
_WORD = re.compile(r"[а-яёәғқңөұүһіa-z0-9]{4,}", re.IGNORECASE)

STOPWORDS = {
    "который", "которая", "которые", "этого", "этому", "будет", "может", "было", "быть",
    "если", "чтобы", "также", "более", "менее", "после", "перед", "между", "через",
    "года", "году", "годов", "текст", "новости", "новость", "вопрос", "ответ", "какой",
    "какая", "какие", "когда", "почему", "нужно", "можно", "всего", "около", "самом",
    "сообщил", "сообщила", "сообщается", "отмечается", "заявил", "казахстан", "казахстана",
    "республики", "республика", "министерство", "правительство",
}


def significant_words(text: str) -> set[str]:
    return {w.lower() for w in _WORD.findall(text or "")} - STOPWORDS


def overlap(a: str, b: str) -> int:
    return len(significant_words(a) & significant_words(b))


def stem(word: str) -> str:
    word = word.lower()
    if len(word) <= 5:
        return word
    cut = len(word) - (2 if len(word) <= 7 else 3 if len(word) <= 9 else 4)
    return word[: max(5, cut)]


def significant_stems(text: str) -> set[str]:
    return {stem(w) for w in significant_words(text)}
