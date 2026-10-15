"""Customer meminta instruksi bayar QRIS untuk ordernya."""

import uuid
from datetime import UTC, datetime

from app.core.security import verify_token
from app.modules.orders.exceptions import OrderNotFoundError
from app.modules.orders.model import OrderStatus, PaymentMethod
from app.modules.orders.repository import OrderRepository
from app.modules.payments.exceptions import (
    PaymentAlreadyPaidError,
    PaymentExpiredError,
    PaymentInvalidStateError,
    PaymentNotQrisError,
)
from app.modules.payments.model import PaymentStatus
from app.modules.payments.provider import PaymentProvider
from app.modules.payments.qris_schema import QrisOut
from app.modules.payments.repository import PaymentRepository


def _has_expired(expires_at: datetime | None) -> bool:
    if expires_at is None:
        return False
    if expires_at.tzinfo is None:  # SQLite membuang info zona waktu
        expires_at = expires_at.replace(tzinfo=UTC)
    return expires_at <= datetime.now(UTC)


class QrisService:
    def __init__(
        self, payments: PaymentRepository, orders: OrderRepository, provider: PaymentProvider
    ) -> None:
        self.payments = payments
        self.orders = orders
        self.provider = provider

    def create_for_order(self, order_id: uuid.UUID, tracking_token: str | None) -> QrisOut:
        order = self.orders.get_by_id(order_id)
        # Token kosong/salah atau order tidak ada: 404 yang sama (tidak membocorkan keberadaan).
        if (
            order is None
            or not tracking_token
            or not verify_token(tracking_token, order.tracking_token_hash)
        ):
            raise OrderNotFoundError
        payment = self.payments.get_latest_by_order(order.id)
        if payment is None or payment.payment_method != PaymentMethod.QRIS.value:
            raise PaymentNotQrisError
        if payment.status == PaymentStatus.PAID.value:
            raise PaymentAlreadyPaidError
        if (
            payment.status != PaymentStatus.PENDING.value
            or order.status != OrderStatus.PENDING.value
        ):
            raise PaymentInvalidStateError
        if _has_expired(payment.expires_at):
            raise PaymentExpiredError

        # Ambil nilai sekarang: setelah commit/rollback objek di session bisa kedaluwarsa.
        payment_id, status, expires_at = payment.id, payment.status, payment.expires_at
        transaction_id = payment.provider_transaction_id
        if transaction_id is None:
            # reference = payment id: kunci idempotensi ke provider, jadi dua permintaan
            # bersamaan tidak menghasilkan dua transaksi berbeda.
            tx = self.provider.create_qris_transaction(
                reference=str(payment_id), amount=payment.amount, expires_at=expires_at
            )
            if self.payments.set_provider_transaction(payment_id, tx.transaction_id):
                self.payments.commit()
                transaction_id = tx.transaction_id
            else:
                self.payments.rollback()  # kalah balapan: pakai transaksi milik pemenang
                winner = self.payments.get_latest_by_order(order.id)
                transaction_id = winner.provider_transaction_id if winner else None
                if transaction_id is None:
                    raise PaymentInvalidStateError
        return QrisOut(
            payment_id=payment_id,
            payment_status=status,
            payment_url=self.provider.payment_url(transaction_id),
            expires_at=expires_at,
        )
