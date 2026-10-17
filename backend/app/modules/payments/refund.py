"""Refund pembayaran CASH oleh ADMIN untuk order yang BELUM dimasak (status CONFIRMED).
Refund penuh saja. Satu transaksi: payment REFUNDED, stok dikembalikan (RESTOCK),
order CANCELLED + riwayat status, dan audit log. Kasir mengembalikan uang secara manual."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.modules.audit.model import AuditLog
from app.modules.inventory.exceptions import ReservationNotActiveError
from app.modules.inventory.service import InventoryService
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import OrderStatus, PaymentMethod
from app.modules.orders.repository import OrderRepository
from app.modules.payments.exceptions import (
    PaymentNotFoundError,
    RefundAmountInvalidError,
    RefundNotAllowedError,
)
from app.modules.payments.model import PaymentStatus
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schema import RefundOut


class _StateChanged(Exception):
    """Payment atau order berubah di tengah jalan (mis. refund lain menang duluan)."""


class PaymentRefundService:
    def __init__(
        self, payments: PaymentRepository, orders: OrderRepository, inventory: InventoryService
    ) -> None:
        self.payments = payments
        self.orders = orders
        self.inventory = inventory

    def refund(
        self, payment_id: uuid.UUID, amount: Decimal, reason: str, admin_id: uuid.UUID
    ) -> RefundOut:
        payment = self.payments.get_by_id(payment_id)
        if payment is None:
            raise PaymentNotFoundError
        if payment.status == PaymentStatus.REFUNDED.value:
            raise RefundNotAllowedError("Pembayaran ini sudah direfund.")
        if payment.status != PaymentStatus.PAID.value:
            raise RefundNotAllowedError("Hanya pembayaran yang sudah lunas yang bisa direfund.")
        if payment.payment_method != PaymentMethod.CASH.value:
            raise RefundNotAllowedError("Refund pembayaran QRIS belum didukung.")
        if amount != payment.amount:
            raise RefundAmountInvalidError(
                {"refundable": str(payment.amount), "requested": str(amount)}
            )
        order = self.orders.get_by_id(payment.order_id)
        if order is None or order.status != OrderStatus.CONFIRMED.value:
            raise RefundNotAllowedError("Order sudah diproses dapur, refund belum didukung.")

        # Ambil sekarang: objek bisa kedaluwarsa setelah commit.
        order_id = order.id
        refunded = payment.amount
        now = datetime.now(UTC)
        try:
            # Urutan kunci sama dengan bayar/batal: payment -> stok -> order.
            if not self.payments.mark_refunded(payment_id):
                raise _StateChanged
            self.inventory.restock_sold(
                order_id, created_by=admin_id, reason=f"Refund order: {reason}"
            )
            if not self.orders.mark_cancelled_after_payment(order_id, now):
                raise _StateChanged
            self.orders.add(
                OrderStatusHistory(
                    order_id=order_id,
                    from_status=OrderStatus.CONFIRMED.value,
                    to_status=OrderStatus.CANCELLED.value,
                    changed_by=admin_id,
                    reason=f"Refund: {reason}",
                )
            )
            self.payments.add(
                AuditLog(
                    user_id=admin_id,
                    action="REFUND_PAYMENT",
                    entity_type="payment",
                    entity_id=payment_id,
                    old_value={"status": PaymentStatus.PAID.value},
                    new_value={
                        "status": PaymentStatus.REFUNDED.value,
                        "amount": str(refunded),
                        "reason": reason,
                        "order_id": str(order_id),
                    },
                )
            )
            self.payments.commit()  # semua atau tidak sama sekali
        except (ReservationNotActiveError, _StateChanged):
            self.payments.rollback()
            raise RefundNotAllowedError(
                "Status pembayaran atau order baru saja berubah. Muat ulang lalu coba lagi."
            ) from None
        except Exception:
            self.payments.rollback()
            raise
        return RefundOut(
            payment_id=payment_id,
            payment_status=PaymentStatus.REFUNDED.value,
            order_status=OrderStatus.CANCELLED.value,
            refunded_amount=refunded,
        )
