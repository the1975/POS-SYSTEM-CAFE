"""Aturan koreksi stok manual oleh ADMIN. Setiap koreksi tercatat di stock_movements."""

import uuid

from app.core.responses import Pagination, build_pagination
from app.modules.inventory.admin_repository import InventoryAdminRepository
from app.modules.inventory.admin_schema import StockAdjustIn, StockAdjustOut, StockItemOut
from app.modules.inventory.exceptions import AdjustExceedsStockError
from app.modules.inventory.model import StockMovement
from app.modules.products.exceptions import ProductNotFoundError
from app.modules.users.model import User


class InventoryAdminService:
    def __init__(self, repo: InventoryAdminRepository) -> None:
        self.repo = repo

    def list_stock(
        self, *, category_id: uuid.UUID | None, search: str | None, page: int, page_size: int
    ) -> tuple[list[StockItemOut], Pagination]:
        rows, total = self.repo.list_stock(
            category_id=category_id, search=search, page=page, page_size=page_size
        )
        items = [
            StockItemOut(
                product_id=product.id,
                product_name=product.name,
                category_name=category.name,
                is_available=product.is_available,
                quantity_available=inv.quantity_available,
                quantity_reserved=inv.quantity_reserved,
                reorder_level=inv.reorder_level,
            )
            for product, category, inv in rows
        ]
        return items, build_pagination(page, page_size, total)

    def adjust(self, product_id: uuid.UUID, data: StockAdjustIn, admin: User) -> StockAdjustOut:
        product = self.repo.get_product(product_id)
        if product is None or self.repo.available_now(product_id) is None:
            raise ProductNotFoundError
        try:
            if not self.repo.adjust_available(product_id, data.quantity):
                raise AdjustExceedsStockError
            self.repo.add(
                StockMovement(
                    product_id=product_id,
                    movement_type=data.movement_type,
                    quantity=data.quantity,
                    reason=data.reason,
                    created_by=admin.id,
                )
            )
            self.repo.commit()
        except Exception:
            self.repo.rollback()
            raise
        return StockAdjustOut(
            product_id=product_id,
            product_name=product.name,
            quantity_available=self.repo.available_now(product_id) or 0,
        )
