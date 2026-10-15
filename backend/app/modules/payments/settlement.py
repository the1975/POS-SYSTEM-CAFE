"""Langkah bersama setelah pembayaran lunas, dipakai cash (kasir) maupun QRIS (webhook):
stok ditahan jadi terjual, order CONFIRMED, riwayat status dicatat.
Berjalan di transaksi milik pemanggil; pemanggil yang commit/rollback."""

import uuid
from datetime import datetime

from app.modules.inventory.service import InventoryService
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import OrderStatus
from app.modules.orders.repository import OrderRepository
from app.modules.payments.exceptions import PaymentInvalidStateError


class OrderSettlement:
    def __init__(self, orders: OrderRepository, inventory: InventoryService) -> None:
        self.orders = orders
        self.inventory = inventory

    def confirm_paid_order(
        self, order_id: uuid.UUID, *, at: datetime, changed_by: uuid.UUID | None, reason: str
    ) -> None:
        """changed_by = None berarti sistem (webhook), bukan staff."""
        self.inventory.convert_reservations(order_id, created_by=changed_by)
        if not self.orders.mark_confirmed(order_id, at):
            raise PaymentInvalidStateError
        self.orders.add(
            OrderStatusHistory(
                order_id=order_id,
                from_status=OrderStatus.PENDING.value,
                to_status=OrderStatus.CONFIRMED.value,
                changed_by=changed_by,
                reason=reason,
            )
        )
