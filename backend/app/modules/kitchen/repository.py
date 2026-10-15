"""Akses database dapur. Pembacaan memakai query kolom (selalu data terbaru dari database);
perubahan status memakai UPDATE bersyarat yang atomik."""

import uuid
from collections import defaultdict
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from app.modules.orders.model import Order, OrderItem, OrderItemStatus, OrderStatus

_ORDER_COLUMNS = (
    Order.id,
    Order.order_number,
    Order.customer_name,
    Order.status,
    Order.confirmed_at,
    Order.preparing_at,
    Order.ready_at,
)


class KitchenRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---- baca ----
    def get_order_row(self, order_id: uuid.UUID, *, lock: bool = False) -> Row | None:
        """lock=True: kunci baris order sampai transaksi selesai (SELECT ... FOR UPDATE),
        supaya dua staff yang bekerja di order yang sama berjalan bergiliran."""
        stmt = select(*_ORDER_COLUMNS).where(Order.id == order_id)
        if lock:
            stmt = stmt.with_for_update()
        return self.db.execute(stmt).first()

    def get_item_row(self, item_id: uuid.UUID) -> Row | None:
        stmt = select(OrderItem.id, OrderItem.order_id, OrderItem.status).where(
            OrderItem.id == item_id
        )
        return self.db.execute(stmt).first()

    def list_order_rows(
        self, statuses: list[str], page: int, page_size: int
    ) -> tuple[list[Row], int]:
        total = (
            self.db.scalar(
                select(func.count()).select_from(Order).where(Order.status.in_(statuses))
            )
            or 0
        )
        stmt = (
            select(*_ORDER_COLUMNS)
            .where(Order.status.in_(statuses))
            # Antrean FIFO: yang lebih dulu dibayar, lebih dulu dikerjakan.
            .order_by(Order.confirmed_at.asc(), Order.created_at.asc(), Order.id.asc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        return list(self.db.execute(stmt)), total

    def items_by_order(self, order_ids: list[uuid.UUID]) -> dict[uuid.UUID, list[Row]]:
        grouped: dict[uuid.UUID, list[Row]] = defaultdict(list)
        if not order_ids:
            return grouped
        stmt = (
            select(
                OrderItem.order_id,
                OrderItem.id,
                OrderItem.product_name_snapshot,
                OrderItem.quantity,
                OrderItem.status,
            )
            .where(OrderItem.order_id.in_(order_ids))
            .order_by(OrderItem.created_at, OrderItem.id)
        )
        for row in self.db.execute(stmt):
            grouped[row.order_id].append(row)
        return grouped

    def count_items_not_ready(self, order_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(OrderItem)
            .where(OrderItem.order_id == order_id, OrderItem.status != OrderItemStatus.READY.value)
        )
        return self.db.scalar(stmt) or 0

    # ---- ubah (atomik) ----
    def start_order(self, order_id: uuid.UUID, at: datetime) -> bool:
        """CONFIRMED -> PREPARING. False bila order sudah tidak CONFIRMED."""
        stmt = (
            update(Order)
            .where(Order.id == order_id, Order.status == OrderStatus.CONFIRMED.value)
            .values(status=OrderStatus.PREPARING.value, preparing_at=at)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def start_items(self, order_id: uuid.UUID) -> int:
        """Item PENDING -> PREPARING (item REMAKE tidak disentuh)."""
        stmt = (
            update(OrderItem)
            .where(
                OrderItem.order_id == order_id, OrderItem.status == OrderItemStatus.PENDING.value
            )
            .values(status=OrderItemStatus.PREPARING.value)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount

    def mark_item_ready(self, item_id: uuid.UUID) -> bool:
        """PREPARING/REMAKE -> READY. False bila item tidak dalam produksi."""
        stmt = (
            update(OrderItem)
            .where(
                OrderItem.id == item_id,
                OrderItem.status.in_(
                    [OrderItemStatus.PREPARING.value, OrderItemStatus.REMAKE.value]
                ),
            )
            .values(status=OrderItemStatus.READY.value)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def mark_order_ready(self, order_id: uuid.UUID, at: datetime) -> bool:
        """PREPARING -> READY. False bila order sudah tidak PREPARING."""
        stmt = (
            update(Order)
            .where(Order.id == order_id, Order.status == OrderStatus.PREPARING.value)
            .values(status=OrderStatus.READY.value, ready_at=at)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def add(self, *objects) -> None:
        for obj in objects:
            self.db.add(obj)
            self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
