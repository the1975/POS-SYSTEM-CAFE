"""Pekerja penanda order OVERDUE.

    python -m app.workers.mark_overdue          # jalan terus, cek berkala
    python -m app.workers.mark_overdue --once   # sekali jalan lalu selesai (cron)

Batas waktu diatur lewat PICKUP_OVERDUE_MINUTES (bawaan 30). Jalankan SATU pekerja saja
untuk satu database (aman kalau dobel, tapi tidak perlu).
"""

import argparse
import logging
import time
from datetime import UTC, datetime

from app.core.config import get_settings
from app.db import models  # noqa: F401  (mendaftarkan semua tabel)
from app.db.session import get_session_factory
from app.modules.orders.overdue import build_overdue_service

logger = logging.getLogger("worker.mark_overdue")


def run_once(batch_size: int = 50) -> int:
    db = get_session_factory()()
    try:
        return build_overdue_service(db).mark_due(datetime.now(UTC), batch_size=batch_size)
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--once", action="store_true", help="sekali jalan lalu selesai")
    args = parser.parse_args()

    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    while True:
        try:
            marked = run_once()
            if marked:
                logger.info("%d order ditandai OVERDUE", marked)
        except Exception:
            logger.exception("Pemeriksaan OVERDUE gagal")
        if args.once:
            return
        time.sleep(settings.expiration_scan_interval_seconds)


if __name__ == "__main__":
    main()
