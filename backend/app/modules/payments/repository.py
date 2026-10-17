"""Akses database pembayaran. Hanya operasi data; aturan bisnis ada di PaymentService."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.modules.payments.model import Payment, PaymentEvent, PaymentStatus


class PaymentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, payment_id: uuid.UUID) -> Payment | None:
        # populate_existing: selalu pakai data terbaru dari database, bukan salinan lama di session.
        stmt = (
            select(Payment)
            .where(Payment.id == payment_id)
            .execution_options(populate_existing=True)
        )
        return self.db.scalar(stmt)

    def mark_cash_paid(
        self, payment_id: uuid.UUID, cash_received: Decimal, change: Decimal, paid_at: datetime
    ) -> bool:
        """WAITING_CASH -> PAID secara ATOMIK. Dua kasir yang klik bersamaan: hanya satu
        yang lolos, yang lain mendapat False (0 baris berubah)."""
        stmt = (
            update(Payment)
            .where(Payment.id == payment_id, Payment.status == PaymentStatus.WAITING_CASH.value)
            .values(
                status=PaymentStatus.PAID.value,
                cash_received=cash_received,
                change_amount=change,
                paid_at=paid_at,
            )
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def get_latest_by_order(self, order_id: uuid.UUID) -> Payment | None:
        stmt = (
            select(Payment)
            .where(Payment.order_id == order_id)
            .order_by(Payment.created_at.desc(), Payment.id.desc())
            .limit(1)
            .execution_options(populate_existing=True)
        )
        return self.db.scalar(stmt)

    def set_provider_transaction(self, payment_id: uuid.UUID, transaction_id: str) -> bool:
        """Simpan ID transaksi provider SEKALI saja (hanya bila masih kosong dan PENDING).
        False = sudah diisi permintaan lain (kalah balapan)."""
        stmt = (
            update(Payment)
            .where(
                Payment.id == payment_id,
                Payment.status == PaymentStatus.PENDING.value,
                Payment.provider_transaction_id.is_(None),
            )
            .values(provider_transaction_id=transaction_id)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def get_by_provider_transaction(self, transaction_id: str) -> Payment | None:
        stmt = (
            select(Payment)
            .where(Payment.provider_transaction_id == transaction_id)
            .execution_options(populate_existing=True)
        )
        return self.db.scalar(stmt)

    def event_exists(self, event_id: str) -> bool:
        stmt = select(PaymentEvent.id).where(PaymentEvent.event_id == event_id).limit(1)
        return self.db.scalar(stmt) is not None

    def add(self, *objects) -> None:
        """Simpan lalu flush: pelanggaran UNIQUE (event_id ganda) langsung terdeteksi."""
        for obj in objects:
            self.db.add(obj)
            self.db.flush()

    def mark_qris_paid(self, payment_id: uuid.UUID, paid_at: datetime) -> bool:
        """PENDING -> PAID secara ATOMIK. False bila sudah tidak PENDING."""
        stmt = (
            update(Payment)
            .where(Payment.id == payment_id, Payment.status == PaymentStatus.PENDING.value)
            .values(status=PaymentStatus.PAID.value, paid_at=paid_at)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def mark_failed(self, payment_id: uuid.UUID) -> bool:
        """PENDING -> FAILED secara ATOMIK. False bila sudah tidak PENDING."""
        stmt = (
            update(Payment)
            .where(Payment.id == payment_id, Payment.status == PaymentStatus.PENDING.value)
            .values(status=PaymentStatus.FAILED.value)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def fail_unpaid_for_order(self, order_id: uuid.UUID) -> int:
        """Pembayaran yang belum lunas (PENDING/WAITING_CASH) jadi FAILED. Yang PAID tidak disentuh."""
        stmt = (
            update(Payment)
            .where(
                Payment.order_id == order_id,
                Payment.status.in_([PaymentStatus.PENDING.value, PaymentStatus.WAITING_CASH.value]),
            )
            .values(status=PaymentStatus.FAILED.value)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount

    def mark_refunded(self, payment_id: uuid.UUID) -> bool:
        """PAID -> REFUNDED secara ATOMIK. Refund ganda: yang kedua mendapat False."""
        stmt = (
            update(Payment)
            .where(Payment.id == payment_id, Payment.status == PaymentStatus.PAID.value)
            .values(status=PaymentStatus.REFUNDED.value)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1
