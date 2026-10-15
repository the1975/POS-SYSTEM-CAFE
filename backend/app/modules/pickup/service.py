"""Aturan bisnis pickup: daftar, verifikasi token, selesaikan.
Alur (database-design §23): Customer tunjukkan token -> Staff scan -> Backend verifikasi ->
cek status order -> penyelesaian ATOMIK. Pickup tidak bisa diselesaikan dua kali."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.engine import Row

from app.core.responses import Pagination, build_pagination
from app.core.security import hash_token
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import OrderStatus
from app.modules.orders.repository import OrderRepository
from app.modules.pickup.exceptions import (
    PickupAlreadyCompletedError,
    PickupInvalidStateError,
    PickupNotFoundError,
    PickupNotVerifiedError,
)
from app.modules.pickup.model import PickupStatus
from app.modules.pickup.repository import PickupRepository
from app.modules.pickup.schema import (
    PickupCompleteOut,
    PickupItemOut,
    PickupOrderOut,
    PickupVerifyOut,
)

# OVERDUE = terlambat diambil, BUKAN batal (spec): tetap boleh diambil.
PICKUP_ORDER_STATUSES = (OrderStatus.READY.value, OrderStatus.OVERDUE.value)


def _items_out(rows: list[Row]) -> list[PickupItemOut]:
    return [PickupItemOut(name=r.product_name_snapshot, quantity=r.quantity) for r in rows]


class PickupService:
    def __init__(self, pickups: PickupRepository, orders: OrderRepository) -> None:
        self.pickups = pickups
        self.orders = orders

    def list_orders(
        self, *, status: OrderStatus, page: int, page_size: int
    ) -> tuple[list[PickupOrderOut], Pagination]:
        rows, total = self.pickups.list_rows(status, page, page_size)
        grouped = self.pickups.items_by_order([row.order_id for row in rows])
        items = [
            PickupOrderOut(
                pickup_id=row.id,
                order_number=row.order_number,
                customer_name=row.customer_name,
                status=row.status,
                ready_at=row.ready_at,
                verified=row.verified_at is not None,
                items=_items_out(grouped.get(row.order_id, [])),
            )
            for row in rows
        ]
        return items, build_pagination(page, page_size, total)

    def verify(self, pickup_token: str, user_id: uuid.UUID) -> PickupVerifyOut:
        # Token tidak pernah disimpan mentah: cari lewat hash-nya. Token salah = 404 yang sama.
        pickup = self.pickups.get_by_token_hash(hash_token(pickup_token))
        if pickup is None:
            raise PickupNotFoundError
        if pickup.status == PickupStatus.COMPLETED.value:
            raise PickupAlreadyCompletedError
        order = self.pickups.get_order_summary(pickup.order_id)
        if order is None or order.status not in PICKUP_ORDER_STATUSES:
            raise PickupInvalidStateError
        try:
            if not self.pickups.record_verification(pickup.id, user_id, datetime.now(UTC)):
                raise PickupAlreadyCompletedError  # selesai di tengah jalan
            self.pickups.commit()
        except Exception:
            self.pickups.rollback()
            raise
        return PickupVerifyOut(
            pickup_id=pickup.id,
            order_number=order.order_number,
            customer_name=order.customer_name,
            status=order.status,
            payment_status=self.orders.latest_payment_status(order.id),
            items=_items_out(self.pickups.items(order.id)),
        )

    def complete(self, pickup_id: uuid.UUID, user_id: uuid.UUID) -> PickupCompleteOut:
        pickup = self.pickups.get_pickup_row(pickup_id)
        if pickup is None:
            raise PickupNotFoundError
        if pickup.status == PickupStatus.COMPLETED.value:
            raise PickupAlreadyCompletedError
        if pickup.verified_at is None:
            raise PickupNotVerifiedError  # tidak boleh melewati verifikasi token
        order = self.pickups.get_order_summary(pickup.order_id)
        if order is None or order.status not in PICKUP_ORDER_STATUSES:
            raise PickupInvalidStateError

        now = datetime.now(UTC)
        try:
            if not self.pickups.complete_pickup(pickup_id, now):
                raise PickupAlreadyCompletedError  # kalah balapan dari staff lain
            if not self.pickups.complete_order(order.id, now):
                raise PickupInvalidStateError
            self.pickups.add(
                OrderStatusHistory(
                    order_id=order.id,
                    from_status=order.status,
                    to_status=OrderStatus.COMPLETED.value,
                    changed_by=user_id,
                    reason="Pesanan diambil customer",
                )
            )
            self.pickups.commit()  # pickup + order + riwayat: semua atau tidak sama sekali
        except Exception:
            self.pickups.rollback()
            raise
        return PickupCompleteOut(
            order_number=order.order_number, status=OrderStatus.COMPLETED.value, completed_at=now
        )
