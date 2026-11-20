"""Akses database stok untuk ADMIN. Hanya query; aturan ada di service."""

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.modules.inventory.model import Inventory
from app.modules.products.model import Category, Product


class InventoryAdminRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_stock(
        self, *, category_id: uuid.UUID | None, search: str | None, page: int, page_size: int
    ) -> tuple[list[tuple[Product, Category, Inventory]], int]:
        filters = []
        if category_id is not None:
            filters.append(Product.category_id == category_id)
        if search:
            filters.append(Product.name.icontains(search, autoescape=True))

        joined = (
            select(Product, Category, Inventory)
            .join(Category, Category.id == Product.category_id)
            .join(Inventory, Inventory.product_id == Product.id)
        )
        total = (
            self.db.scalar(
                select(func.count())
                .select_from(Product)
                .join(Category, Category.id == Product.category_id)
                .join(Inventory, Inventory.product_id == Product.id)
                .where(*filters)
            )
            or 0
        )
        stmt = (
            joined.where(*filters)
            .order_by(Category.sort_order, Product.name, Product.id)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        return [(r[0], r[1], r[2]) for r in self.db.execute(stmt)], total

    def get_product(self, product_id: uuid.UUID) -> Product | None:
        return self.db.get(Product, product_id)

    def adjust_available(self, product_id: uuid.UUID, delta: int) -> bool:
        """Ubah stok tersedia secara ATOMIK. Gagal (False) bila hasilnya akan minus
        atau produk belum punya record inventory."""
        stmt = (
            update(Inventory)
            .where(
                Inventory.product_id == product_id,
                Inventory.quantity_available + delta >= 0,
            )
            .values(quantity_available=Inventory.quantity_available + delta)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def available_now(self, product_id: uuid.UUID) -> int | None:
        return self.db.scalar(
            select(Inventory.quantity_available).where(Inventory.product_id == product_id)
        )

    def get_reorder_level(self, product_id: uuid.UUID) -> int | None:
        return self.db.scalar(
            select(Inventory.reorder_level).where(Inventory.product_id == product_id)
        )

    def set_reorder_level(self, product_id: uuid.UUID, level: int) -> bool:
        stmt = (
            update(Inventory)
            .where(Inventory.product_id == product_id)
            .values(reorder_level=level)
            .execution_options(synchronize_session=False)
        )
        return self.db.execute(stmt).rowcount == 1

    def add(self, *objects) -> None:
        self.db.add_all(objects)
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
