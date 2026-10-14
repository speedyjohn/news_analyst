from functools import lru_cache
from pathlib import Path

_DIR = Path(__file__).parent / "prompts"


@lru_cache
def load_prompt(name: str) -> str:
    path = _DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Нет промпта {path}")
    return path.read_text(encoding="utf-8").strip()
