"""Pekerja kedaluwarsa reservasi stok.

    python -m app.workers.expire_reservations          # jalan terus, cek berkala
    python -m app.workers.expire_reservations --once   # sekali jalan lalu selesai (cron)

Jalankan SATU pekerja saja untuk satu database (aman kalau dobel, tapi tidak perlu).
"""

import argparse
import logging
import time
from datetime import UTC, datetime

from app.core.config import get_settings
from app.db import models  # noqa: F401  (mendaftarkan semua tabel)
from app.db.session import get_session_factory
from app.modules.orders.expiration import build_expiration_service

logger = logging.getLogger("worker.expire_reservations")


def run_once(batch_size: int = 50) -> int:
    db = get_session_factory()()
    try:
        return build_expiration_service(db).expire_due(datetime.now(UTC), batch_size=batch_size)
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
            expired = run_once()
            if expired:
                logger.info("%d order dikedaluwarsakan, stok dikembalikan", expired)
        except Exception:
            # Database sempat tidak terjangkau dsb.: jangan mati, coba lagi di putaran berikut.
            logger.exception("Pemeriksaan kedaluwarsa gagal")
        if args.once:
            return
        time.sleep(settings.expiration_scan_interval_seconds)


if __name__ == "__main__":
    main()
