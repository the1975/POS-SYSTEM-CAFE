"""Aturan bisnis dapur: antrean, mulai memasak, tandai item siap.
Order jadi READY hanya bila SEMUA item READY (spec); saat itu record pickup dibuat."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.engine import Row

from app.core.responses import Pagination, build_pagination
from app.core.security import derive_pickup_token, hash_token
from app.modules.kitchen.exceptions import (
    KitchenInvalidStateError,
    OrderItemNotFoundError,
    OrderNotPaidError,
)
from app.modules.kitchen.repository import KitchenRepository
from app.modules.kitchen.schema import KitchenItemOut, KitchenOrderOut
from app.modules.orders.exceptions import OrderNotFoundError
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import OrderItemStatus, OrderStatus
from app.modules.orders.repository import OrderRepository
from app.modules.payments.model import PaymentStatus
from app.modules.pickup.model import Pickup
from app.modules.pickup.repository import PickupRepository


class KitchenService:
    def __init__(
        self, kitchen: KitchenRepository, orders: OrderRepository, pickups: PickupRepository
    ) -> None:
        self.kitchen = kitchen
        self.orders = orders
        self.pickups = pickups

    # ---- antrean ----
    def list_orders(
        self, *, status: OrderStatus | None, page: int, page_size: int
    ) -> tuple[list[KitchenOrderOut], Pagination]:
        # Tanpa filter: antrean aktif dapur (sudah dibayar, belum selesai dimasak).
        statuses = (
            [status.value] if status else [OrderStatus.CONFIRMED.value, OrderStatus.PREPARING.value]
        )
        rows, total = self.kitchen.list_order_rows(statuses, page, page_size)
        grouped = self.kitchen.items_by_order([row.id for row in rows])
        items = [self._to_out(row, grouped.get(row.id, [])) for row in rows]
        return items, build_pagination(page, page_size, total)

    # ---- mulai memasak: CONFIRMED -> PREPARING ----
    def start_order(self, order_id: uuid.UUID, user_id: uuid.UUID) -> KitchenOrderOut:
        now = datetime.now(UTC)
        try:
            order = self.kitchen.get_order_row(order_id, lock=True)
            if order is None:
                raise OrderNotFoundError
            if order.status == OrderStatus.PREPARING.value:
                self.kitchen.rollback()  # sudah dimulai: tidak ada yang berubah, lepas kunci
                return self._view(order_id)
            if order.status != OrderStatus.CONFIRMED.value:
                raise KitchenInvalidStateError
            if self.orders.latest_payment_status(order_id) != PaymentStatus.PAID.value:
                raise OrderNotPaidError
            if not self.kitchen.start_order(order_id, now):
                raise KitchenInvalidStateError
            self.kitchen.start_items(order_id)
            self.kitchen.add(
                OrderStatusHistory(
                    order_id=order_id,
                    from_status=OrderStatus.CONFIRMED.value,
                    to_status=OrderStatus.PREPARING.value,
                    changed_by=user_id,
                    reason="Dapur mulai memproses",
                )
            )
            self.kitchen.commit()
        except Exception:
            self.kitchen.rollback()
            raise
        return self._view(order_id)

    # ---- tandai item siap; semua siap -> order READY + pickup ----
    def mark_item_ready(self, item_id: uuid.UUID, user_id: uuid.UUID) -> KitchenOrderOut:
        item = self.kitchen.get_item_row(item_id)
        if item is None:
            raise OrderItemNotFoundError
        order_id = item.order_id
        now = datetime.now(UTC)
        try:
            # Kunci order dulu: dua item terakhir yang ditandai bersamaan tidak boleh sama-sama
            # merasa "masih ada yang belum siap" (order nyangkut di PREPARING).
            order = self.kitchen.get_order_row(order_id, lock=True)
            item = self.kitchen.get_item_row(item_id)  # baca ulang: bisa berubah saat menunggu
            if order is None or item is None:
                raise OrderItemNotFoundError
            if item.status == OrderItemStatus.READY.value:
                self.kitchen.rollback()  # sudah siap: tidak ada yang berubah, lepas kunci
                return self._view(order_id)
            if order.status != OrderStatus.PREPARING.value:
                raise KitchenInvalidStateError
            if not self.kitchen.mark_item_ready(item_id):
                raise KitchenInvalidStateError
            if self.kitchen.count_items_not_ready(order_id) == 0:
                self._finish_order(order_id, user_id, now)
            self.kitchen.commit()
        except Exception:
            self.kitchen.rollback()
            raise
        return self._view(order_id)

    def _finish_order(self, order_id: uuid.UUID, user_id: uuid.UUID, now: datetime) -> None:
        if not self.kitchen.mark_order_ready(order_id, now):
            raise KitchenInvalidStateError
        self.kitchen.add(
            OrderStatusHistory(
                order_id=order_id,
                from_status=OrderStatus.PREPARING.value,
                to_status=OrderStatus.READY.value,
                changed_by=user_id,
                reason="Semua item siap",
            )
        )
        # Hanya HASH token yang disimpan; token asli diturunkan lagi saat customer melihatnya.
        token_hash = hash_token(derive_pickup_token(order_id))
        self.pickups.add(Pickup(order_id=order_id, pickup_token_hash=token_hash))

    # ---- tampilan ----
    def _view(self, order_id: uuid.UUID) -> KitchenOrderOut:
        row = self.kitchen.get_order_row(order_id)
        if row is None:
            raise OrderNotFoundError
        return self._to_out(row, self.kitchen.items_by_order([order_id]).get(order_id, []))

    @staticmethod
    def _to_out(row: Row, items: list[Row]) -> KitchenOrderOut:
        return KitchenOrderOut(
            order_id=row.id,
            order_number=row.order_number,
            customer_name=row.customer_name,
            status=row.status,
            confirmed_at=row.confirmed_at,
            preparing_at=row.preparing_at,
            ready_at=row.ready_at,
            items=[
                KitchenItemOut(
                    order_item_id=i.id,
                    name=i.product_name_snapshot,
                    quantity=i.quantity,
                    status=i.status,
                )
                for i in items
            ],
        )
