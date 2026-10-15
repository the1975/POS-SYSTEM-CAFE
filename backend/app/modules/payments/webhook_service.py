"""Webhook payment provider. Satu transaksi: catat event + ubah payment + (bila lunas)
stok terjual, order CONFIRMED, riwayat status. Aman dikirim berulang (idempotent)."""

from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError

from app.modules.inventory.service import InventoryService
from app.modules.orders.model import OrderStatus
from app.modules.orders.repository import OrderRepository
from app.modules.payments.exceptions import (
    InvalidWebhookSignatureError,
    PaymentAmountMismatchError,
    PaymentInvalidStateError,
    PaymentNotFoundError,
)
from app.modules.payments.model import Payment, PaymentEvent, PaymentStatus
from app.modules.payments.provider import (
    EVENT_FAILED,
    EVENT_PAID,
    PaymentProvider,
    ProviderEvent,
)
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.settlement import OrderSettlement
from app.modules.payments.webhook_schema import WebhookOut


class WebhookService:
    def __init__(
        self,
        payments: PaymentRepository,
        orders: OrderRepository,
        inventory: InventoryService,
        provider: PaymentProvider,
    ) -> None:
        self.payments = payments
        self.orders = orders
        self.provider = provider
        self.settlement = OrderSettlement(orders, inventory)

    def handle(self, raw_body: bytes, signature: str | None) -> WebhookOut:
        # 1) Keaslian dulu, sebelum isi body disentuh.
        if not self.provider.verify_webhook(raw_body=raw_body, signature=signature):
            raise InvalidWebhookSignatureError
        event = self.provider.parse_webhook(raw_body)
        payment = self.payments.get_by_provider_transaction(event.transaction_id)
        if payment is None:
            raise PaymentNotFoundError
        # 2) Event yang sama tidak boleh menjalankan logika dua kali.
        if self.payments.event_exists(event.event_id):
            return WebhookOut(result="duplicate")

        now = datetime.now(UTC)
        try:
            record = PaymentEvent(
                payment_id=payment.id,
                event_id=event.event_id,
                event_type=event.event_type,
                payload=event.payload,
            )
            self.payments.add(record)  # UNIQUE event_id: dua webhook bersamaan, satu yang menang
            result = self._apply(payment, event, now)
            if result == "processed":
                record.processed_at = now
            self.payments.commit()  # event + payment + stok + order: semua atau tidak sama sekali
        except IntegrityError:
            self.payments.rollback()
            if self.payments.event_exists(event.event_id):
                return WebhookOut(result="duplicate")
            raise
        except Exception:
            self.payments.rollback()  # event ikut dibatalkan, provider boleh kirim ulang
            raise
        return WebhookOut(result=result)

    def _apply(self, payment: Payment, event: ProviderEvent, now: datetime) -> str:
        if event.event_type == EVENT_PAID:
            if event.amount != payment.amount:
                raise PaymentAmountMismatchError(
                    {"expected": str(payment.amount), "received": str(event.amount)}
                )
            if payment.status == PaymentStatus.PAID.value:
                return "ignored"  # event lain untuk pembayaran yang sudah lunas
            if payment.status != PaymentStatus.PENDING.value:
                raise PaymentInvalidStateError
            order = self.orders.get_by_id(payment.order_id)
            if order is None or order.status != OrderStatus.PENDING.value:
                raise PaymentInvalidStateError
            if not self.payments.mark_qris_paid(payment.id, now):
                raise PaymentInvalidStateError
            self.settlement.confirm_paid_order(
                order.id, at=now, changed_by=None, reason="Pembayaran QRIS lunas (webhook)"
            )
            return "processed"
        if event.event_type == EVENT_FAILED:
            # Pelepasan stok untuk pembayaran gagal ditangani di tahap kedaluwarsa/pembatalan.
            return "processed" if self.payments.mark_failed(payment.id) else "ignored"
        return "ignored"  # jenis event lain: dicatat saja
