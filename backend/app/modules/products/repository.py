"""Akses database untuk menu. Hanya query; aturan bisnis ada di service."""

import uuid

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.inventory.model import Inventory
from app.modules.products.model import Category, Product
from app.modules.products.schema import ProductSort


class MenuRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active_categories(self) -> list[Category]:
        stmt = select(Category).where(Category.is_active.is_(True))
        return list(self.db.scalars(stmt.order_by(Category.sort_order, Category.name)))

    def get_active_category(self, category_id: uuid.UUID) -> Category | None:
        stmt = select(Category).where(Category.id == category_id, Category.is_active.is_(True))
        return self.db.scalar(stmt)

    def _visible(self, *columns) -> Select:
        """Produk yang boleh dilihat customer: tersedia DAN kategorinya aktif.
        Inventory di-LEFT JOIN: produk tanpa record inventory tetap tampil (in_stock=false)."""
        return (
            select(*columns)
            .select_from(Product)
            .join(Category, Category.id == Product.category_id)
            .outerjoin(Inventory, Inventory.product_id == Product.id)
            .where(Product.is_available.is_(True), Category.is_active.is_(True))
        )

    @staticmethod
    def _in_stock():
        return func.coalesce(Inventory.quantity_available, 0) > 0

    def search_visible(
        self,
        *,
        category_id: uuid.UUID | None,
        search: str | None,
        sort: ProductSort,
        page: int,
        page_size: int,
    ) -> tuple[list[tuple[Product, bool]], int]:
        filters = []
        if category_id is not None:
            filters.append(Product.category_id == category_id)
        if search:
            # autoescape: karakter % dan _ dari user dianggap teks biasa, bukan wildcard.
            filters.append(Product.name.icontains(search, autoescape=True))

        total = self.db.scalar(self._visible(func.count(Product.id)).where(*filters)) or 0

        if sort is ProductSort.PRICE_ASC:
            order = (Product.price.asc(), Product.name)
        elif sort is ProductSort.PRICE_DESC:
            order = (Product.price.desc(), Product.name)
        else:
            order = (Category.sort_order, Product.name)

        stmt = (
            self._visible(Product, self._in_stock().label("in_stock"))
            .where(*filters)
            # Product.id sebagai pembeda terakhir: urutan stabil antar halaman.
            .order_by(*order, Product.id)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        rows = [(row[0], bool(row[1])) for row in self.db.execute(stmt)]
        return rows, total

    def get_visible(self, product_id: uuid.UUID) -> tuple[Product, bool] | None:
        stmt = self._visible(Product, self._in_stock().label("in_stock")).where(
            Product.id == product_id
        )
        row = self.db.execute(stmt).first()
        return (row[0], bool(row[1])) if row else None
