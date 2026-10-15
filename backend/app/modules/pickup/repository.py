"""Akses database pickup. Pembacaan memakai query kolom (selalu data terbaru dari database);
perubahan status memakai UPDATE bersyarat yang atomik."""

import uuid
from collections import defaultdict
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from app.modules.orders.model import Order, OrderItem, OrderStatus
from app.modules.pickup.model import Pickup, PickupStatus

_PICKUP_COLUMNS = (Pickup.id, Pickup.order_id, Pickup.status, Pickup.verified_at)


class PickupRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---- baca ----
    def get_by_token_hash(self, token_hash: str) -> Row | None:
        stmt = select(*_PICKUP_COLUMNS).where(Pickup.pickup_token_hash == token_hash)
        return self.db.execute(stmt).first()

    def get_pickup_row(self, pickup_id: uuid.UUID) -> Row | None:
        stmt = select(*_PICKUP_COLUMNS).where(Pickup.id == pickup_id)
        return self.db.execute(stmt).first()

    def get_order_summary(self, order_id: uuid.UUID) -> Row | None:
        stmt = select(
            Order.id, Order.order_number, Order.customer_name, Order.status, Order.ready_at
        ).where(Order.id == order_id)
        return self.db.execute(stmt).first()

    def items(self, order_id: uuid.UUID) -> list[Row]:
        stmt = (
            select(OrderItem.product_name_snapshot, OrderItem.quantity)
            .where(OrderItem.order_id == order_id)
            .order_by(OrderItem.created_at, OrderItem.id)
        )
        return list(self.db.execute(stmt))

    def list_rows(self, status: OrderStatus, page: int, page_size: int) -> tuple[list[Row], int]:
        join_on = Order.id == Pickup.order_id
        total = (
            self.db.scalar(
                select(func.count())
                .select_from(Pickup)
                .join(Order, join_on)
                .where(Order.status == status.value)
            )
            or 0
        )
        stmt = (
            select(
                Pickup.id,
                Pickup.verified_at,
                Order.id.label("order_id"),
                Order.order_number,
                Order.customer_name,
                Order.status,
                Order.ready_at,
            )
            .join(Order, join_on)
            .where(Order.status == status.value)
            # Yang lebih dulu siap, lebih dulu dilayani.
            .order_by(Order.ready_at.asc(), Order.id.asc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        return list(self.db.execute(stmt)), total

    def items_by_order(self, order_ids: list[uuid.UUID]) -> dict[uuid.UUID, list[Row]]:
        grouped: dict[uuid.UUID, list[Row]] = defaultdict(list)
        if not order_ids:
            return grouped
        stmt = (
            select(OrderItem.order_id, OrderItem.product_name_snapshot, OrderItem.quantity)
            .where(OrderItem.order_id.in_(order_ids))
            .order_by(OrderItem.created_at, OrderItem.id)
        )
        for row in self.db.execute(stmt):
            grouped[row.order_id].append(row)
        return grouped

    # ---- ubah (atomik) ----
    def record_verification(self, pickup_id: uuid.UUID, user_id: uuid.UUID, at: datetime) -> bool:
        """Catat siapa dan kapan memverifikasi. False bila pickup sudah tidak WAITING_PICKUP."""
        stmt = (
            update(Pickup)
            .where(Pickup.id == pickup_id, Pickup.status == PickupStatus.WAITING_PICKUP.value)
            .values(verified_by=user_id, verified_at=at)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def complete_pickup(self, pickup_id: uuid.UUID, at: datetime) -> bool:
        """WAITING_PICKUP -> COMPLETED secara ATOMIK. Dua staff bersamaan: hanya satu yang True."""
        stmt = (
            update(Pickup)
            .where(Pickup.id == pickup_id, Pickup.status == PickupStatus.WAITING_PICKUP.value)
            .values(status=PickupStatus.COMPLETED.value, completed_at=at)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def complete_order(self, order_id: uuid.UUID, at: datetime) -> bool:
        """READY/OVERDUE -> COMPLETED. False bila order tidak dalam status pickup."""
        stmt = (
            update(Order)
            .where(
                Order.id == order_id,
                Order.status.in_([OrderStatus.READY.value, OrderStatus.OVERDUE.value]),
            )
            .values(status=OrderStatus.COMPLETED.value, completed_at=at)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def add(self, *objects) -> None:
        """Simpan sesuai urutan, satu flush per objek (pelanggaran UNIQUE langsung terdeteksi)."""
        for obj in objects:
            self.db.add(obj)
            self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
