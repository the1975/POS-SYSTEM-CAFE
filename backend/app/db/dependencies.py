from collections.abc import Iterator

from sqlalchemy.orm import Session

from app.db.session import get_session_factory


def get_db() -> Iterator[Session]:
    """Satu session per request. Commit/rollback dikontrol service (unit of work),
    bukan otomatis di sini."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
