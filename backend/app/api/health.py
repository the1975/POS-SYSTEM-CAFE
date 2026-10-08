import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.dependencies import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def liveness() -> dict:
    """Proses hidup. Tidak menyentuh database."""
    return {"status": "ok"}


@router.get("/ready")
def readiness(db: Annotated[Session, Depends(get_db)]) -> dict:
    """Siap melayani: database bisa dijangkau."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        # Detail koneksi tidak dibocorkan; log lengkap ada di server.
        logger.exception("Readiness check failed", exc_info=exc)
        raise HTTPException(status_code=503, detail="Database tidak tersedia.") from exc
    return {"status": "ready"}
