import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.db import session_scope  # noqa: E402
from app.services import ingestion  # noqa: E402


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    only = sys.argv[1] if len(sys.argv) > 1 else None
    with session_scope() as session:
        print("Обновлено:", ingestion.refetch_texts(session, only=only))


if __name__ == "__main__":
    main()
