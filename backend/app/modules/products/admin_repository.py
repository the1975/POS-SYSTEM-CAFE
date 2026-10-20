"""Akses database untuk pengelolaan produk oleh ADMIN. Hanya query; aturan ada di service."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.products.model import Category, Product


class ProductAdminRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_product(self, product_id: uuid.UUID) -> Product | None:
        # Semua produk (termasuk yang disembunyikan): admin perlu bisa mengaktifkannya lagi.
        return self.db.get(Product, product_id)

    def get_category(self, category_id: uuid.UUID) -> Category | None:
        return self.db.get(Category, category_id)

    def list_for_admin(
        self,
        *,
        category_id: uuid.UUID | None,
        is_available: bool | None,
        search: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[tuple[Product, str]], int]:
        """SEMUA produk (tersedia maupun disembunyikan, kategori aktif maupun tidak)."""
        filters = []
        if category_id is not None:
            filters.append(Product.category_id == category_id)
        if is_available is not None:
            filters.append(Product.is_available.is_(is_available))
        if search:
            # autoescape: karakter % dan _ dari user dianggap teks biasa, bukan wildcard.
            filters.append(Product.name.icontains(search, autoescape=True))

        base = select(Product, Category.name).join(Category, Category.id == Product.category_id)
        total = (
            self.db.scalar(
                select(func.count())
                .select_from(Product)
                .join(Category, Category.id == Product.category_id)
                .where(*filters)
            )
            or 0
        )
        stmt = (
            base.where(*filters)
            # Product.id sebagai pembeda terakhir: urutan stabil antar halaman.
            .order_by(Category.sort_order, Product.name, Product.id)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        return [(row[0], row[1]) for row in self.db.execute(stmt)], total

    def add(self, *objects) -> None:
        self.db.add_all(objects)
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
