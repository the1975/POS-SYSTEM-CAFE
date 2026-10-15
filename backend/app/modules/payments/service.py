"""Aturan bisnis pembayaran cash oleh kasir. Konfirmasi = satu transaksi:
payment PAID + (lewat OrderSettlement) stok terjual, order CONFIRMED, riwayat status."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.modules.inventory.service import InventoryService
from app.modules.orders.model import OrderStatus, PaymentMethod
from app.modules.orders.repository import OrderRepository
from app.modules.payments.exceptions import (
    InsufficientCashError,
    PaymentAlreadyPaidError,
    PaymentInvalidStateError,
    PaymentNotCashError,
    PaymentNotFoundError,
)
from app.modules.payments.model import PaymentStatus
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schema import CashConfirmOut
from app.modules.payments.settlement import OrderSettlement


class PaymentService:
    def __init__(
        self, payments: PaymentRepository, orders: OrderRepository, inventory: InventoryService
    ) -> None:
        self.payments = payments
        self.orders = orders
        self.settlement = OrderSettlement(orders, inventory)

    def confirm_cash(
        self, payment_id: uuid.UUID, cash_received: Decimal, cashier_id: uuid.UUID
    ) -> CashConfirmOut:
        payment = self.payments.get_by_id(payment_id)
        if payment is None:
            raise PaymentNotFoundError
        if payment.payment_method != PaymentMethod.CASH.value:
            raise PaymentNotCashError
        if payment.status == PaymentStatus.PAID.value:
            raise PaymentAlreadyPaidError
        if payment.status != PaymentStatus.WAITING_CASH.value:
            raise PaymentInvalidStateError
        if cash_received < payment.amount:
            raise InsufficientCashError(
                {"required": str(payment.amount), "received": str(cash_received)}
            )
        order = self.orders.get_by_id(payment.order_id)
        if order is None or order.status != OrderStatus.PENDING.value:
            raise PaymentInvalidStateError

        change = cash_received - payment.amount  # dihitung backend, bukan dari client
        now = datetime.now(UTC)
        try:
            if not self.payments.mark_cash_paid(payment.id, cash_received, change, now):
                raise PaymentAlreadyPaidError  # kalah balapan dari konfirmasi lain
            self.settlement.confirm_paid_order(
                order.id,
                at=now,
                changed_by=cashier_id,
                reason="Pembayaran cash dikonfirmasi kasir",
            )
            self.payments.commit()  # semua atau tidak sama sekali
        except Exception:
            self.payments.rollback()
            raise
        return CashConfirmOut(
            payment_id=payment.id,
            payment_status=PaymentStatus.PAID.value,
            order_status=OrderStatus.CONFIRMED.value,
            amount=payment.amount,
            cash_received=cash_received,
            change=change,
        )
