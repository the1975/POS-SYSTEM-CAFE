"""Akses database untuk pengelolaan produk oleh ADMIN. Hanya query; aturan ada di service."""

import uuid

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

    def add(self, *objects) -> None:
        self.db.add_all(objects)
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
