"""Akses database untuk order. Hanya query/penyimpanan; aturan bisnis ada di service."""

import uuid
from datetime import datetime

from sqlalchemy import Sequence, select, update
from sqlalchemy.orm import Session, selectinload

from app.modules.orders.model import Order, OrderStatus
from app.modules.payments.model import Payment
from app.modules.pickup.model import Pickup
from app.modules.products.model import Category, Product

# SEQUENCE PostgreSQL (dibuat di migrasi): nextval atomik, aman untuk request paralel.
ORDER_NUMBER_SEQUENCE = Sequence("order_number_seq")


class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def next_order_sequence(self) -> int:
        return self.db.scalar(select(ORDER_NUMBER_SEQUENCE.next_value()))

    def get_orderable_products(self, product_ids: list[uuid.UUID]) -> dict[uuid.UUID, Product]:
        """Produk yang boleh dipesan: tersedia DAN kategorinya aktif. Harga diambil dari sini."""
        stmt = (
            select(Product)
            .join(Category, Category.id == Product.category_id)
            .where(
                Product.id.in_(product_ids),
                Product.is_available.is_(True),
                Category.is_active.is_(True),
            )
        )
        return {p.id: p for p in self.db.scalars(stmt)}

    def find_by_idempotency_key(self, key: str) -> Order | None:
        stmt = select(Order).where(Order.idempotency_key == key).options(selectinload(Order.items))
        return self.db.scalar(stmt)

    def get_by_id(self, order_id: uuid.UUID) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
            # Selalu data terbaru dari DB, bukan salinan lama di session (update massal
            # seperti mark_confirmed tidak memperbarui objek yang sudah ada di session).
            .execution_options(populate_existing=True)
        )
        return self.db.scalar(stmt)

    def add(self, *objects) -> None:
        """Simpan SESUAI URUTAN argumen (satu flush per objek).
        Penting: tabel tanpa relationship ke induknya (mis. order_status_history) tidak dikenali
        urutannya oleh SQLAlchemy, padahal PostgreSQL menegakkan foreign key. Jadi induk
        harus diberikan lebih dulu."""
        for obj in objects:
            self.db.add(obj)
            self.db.flush()  # kirim ke DB; pelanggaran unique/FK terdeteksi sebelum commit

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def mark_confirmed(self, order_id: uuid.UUID, at: datetime) -> bool:
        """PENDING -> CONFIRMED secara ATOMIK. False bila order sudah tidak PENDING."""
        stmt = (
            update(Order)
            .where(Order.id == order_id, Order.status == OrderStatus.PENDING.value)
            .values(status=OrderStatus.CONFIRMED.value, confirmed_at=at)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def latest_payment_status(self, order_id: uuid.UUID) -> str | None:
        """Status pembayaran terbaru order ini (None bila belum ada tagihan)."""
        stmt = (
            select(Payment.status)
            .where(Payment.order_id == order_id)
            .order_by(Payment.created_at.desc(), Payment.id.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def mark_cancelled(self, order_id: uuid.UUID, at: datetime) -> bool:
        """PENDING -> CANCELLED secara ATOMIK. False bila order sudah tidak PENDING."""
        stmt = (
            update(Order)
            .where(Order.id == order_id, Order.status == OrderStatus.PENDING.value)
            .values(status=OrderStatus.CANCELLED.value, cancelled_at=at)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def pickup_status(self, order_id: uuid.UUID) -> str | None:
        """Status pickup order ini (None bila belum ada pickup)."""
        return self.db.scalar(select(Pickup.status).where(Pickup.order_id == order_id))
