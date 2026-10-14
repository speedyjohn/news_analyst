import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.db import session_scope  # noqa: E402
from app.services import sources  # noqa: E402


# запускать до gunicorn, иначе воркеры одновременно вставляют одни и те же источники
def main() -> None:
    with session_scope() as session:
        sources.sync_from_yaml(session)


if __name__ == "__main__":
    main()
