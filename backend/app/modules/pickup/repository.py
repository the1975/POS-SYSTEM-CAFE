"""Akses database pickup. (Verifikasi dan penyelesaian pickup menyusul di tahap berikutnya.)"""

from sqlalchemy.orm import Session

from app.modules.pickup.model import Pickup


class PickupRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, pickup: Pickup) -> None:
        """Simpan lalu flush: pelanggaran UNIQUE (order sudah punya pickup) langsung terdeteksi."""
        self.db.add(pickup)
        self.db.flush()
