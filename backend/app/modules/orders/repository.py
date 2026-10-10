"""Akses database untuk order. Hanya query/penyimpanan; aturan bisnis ada di service."""
import uuid

from sqlalchemy import Sequence, select
from sqlalchemy.orm import Session, selectinload

from app.modules.orders.model import Order
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
        stmt = select(Order).where(Order.id == order_id).options(selectinload(Order.items))
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
