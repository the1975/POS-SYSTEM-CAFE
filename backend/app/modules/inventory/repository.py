"""Akses database stok. Hanya operasi data; aturan bisnis ada di InventoryService."""

import uuid
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.modules.inventory.model import Inventory, ReservationStatus, StockReservation


class InventoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def try_reserve(self, product_id: uuid.UUID, quantity: int) -> bool:
        """Tahan stok secara ATOMIK dalam satu perintah UPDATE bersyarat.

        Bukan "baca stok lalu tulis ulang": dua customer yang berebut unit terakhir tidak
        bisa sama-sama lolos, karena database mengunci barisnya dan hanya satu UPDATE yang
        memenuhi syarat (quantity_available >= quantity). Jumlah baris terubah = 0 -> stok kurang.
        """
        stmt = (
            update(Inventory)
            .where(Inventory.product_id == product_id, Inventory.quantity_available >= quantity)
            .values(
                quantity_available=Inventory.quantity_available - quantity,
                quantity_reserved=Inventory.quantity_reserved + quantity,
            )
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def available_quantities(self, product_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
        stmt = select(Inventory.product_id, Inventory.quantity_available).where(
            Inventory.product_id.in_(product_ids)
        )
        return {pid: qty for pid, qty in self.db.execute(stmt)}

    def add(self, *objects) -> None:
        self.db.add_all(objects)
        self.db.flush()

    def rollback(self) -> None:
        self.db.rollback()

    def active_reservations(self, order_id: uuid.UUID) -> list[StockReservation]:
        stmt = select(StockReservation).where(
            StockReservation.order_id == order_id,
            StockReservation.status == ReservationStatus.ACTIVE.value,
        )
        return list(self.db.scalars(stmt))

    def consume_reserved(self, product_id: uuid.UUID, quantity: int) -> bool:
        """Kurangi stok ditahan (barang terjual) secara ATOMIK; gagal kalau reserved kurang."""
        stmt = (
            update(Inventory)
            .where(Inventory.product_id == product_id, Inventory.quantity_reserved >= quantity)
            .values(quantity_reserved=Inventory.quantity_reserved - quantity)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def mark_reservations_converted(self, order_id: uuid.UUID) -> int:
        """ACTIVE -> CONVERTED. Hanya yang masih ACTIVE yang berubah; mengembalikan jumlahnya."""
        stmt = (
            update(StockReservation)
            .where(
                StockReservation.order_id == order_id,
                StockReservation.status == ReservationStatus.ACTIVE.value,
            )
            .values(status=ReservationStatus.CONVERTED.value)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount

    def due_reservation_order_ids(self, now: datetime, limit: int) -> list[uuid.UUID]:
        """Order yang punya reservasi ACTIVE dan batas waktunya sudah lewat (paling lama dulu)."""
        stmt = (
            select(StockReservation.order_id)
            .where(
                StockReservation.status == ReservationStatus.ACTIVE.value,
                StockReservation.expires_at <= now,
            )
            .group_by(StockReservation.order_id)
            .order_by(func.min(StockReservation.expires_at))
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def release_reserved(self, product_id: uuid.UUID, quantity: int) -> bool:
        """Kembalikan stok ditahan ke tersedia secara ATOMIK; gagal kalau reserved kurang."""
        stmt = (
            update(Inventory)
            .where(Inventory.product_id == product_id, Inventory.quantity_reserved >= quantity)
            .values(
                quantity_reserved=Inventory.quantity_reserved - quantity,
                quantity_available=Inventory.quantity_available + quantity,
            )
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def mark_reservations_released(
        self, order_id: uuid.UUID, status: ReservationStatus, at: datetime
    ) -> int:
        """ACTIVE -> EXPIRED/CANCELLED. Hanya yang masih ACTIVE yang berubah; mengembalikan jumlahnya."""
        stmt = (
            update(StockReservation)
            .where(
                StockReservation.order_id == order_id,
                StockReservation.status == ReservationStatus.ACTIVE.value,
            )
            .values(status=status.value, released_at=at)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount
