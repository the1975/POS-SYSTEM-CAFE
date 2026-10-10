"""Aturan bisnis menu customer. Tidak tahu soal HTTP maupun SQL."""
import uuid

from app.core.responses import Pagination, build_pagination
from app.modules.products.exceptions import CategoryNotFoundError, ProductNotFoundError
from app.modules.products.model import Product
from app.modules.products.repository import MenuRepository
from app.modules.products.schema import CategoryOut, ProductOut, ProductSort


def _to_product_out(product: Product, in_stock: bool) -> ProductOut:
    # Dipetakan manual (bukan from_attributes) supaya cost_price tidak mungkin ikut bocor.
    return ProductOut(
        id=product.id,
        category_id=product.category_id,
        name=product.name,
        description=product.description,
        price=product.price,
        image_url=product.image_url,
        is_available=product.is_available,
        in_stock=in_stock,
    )


class MenuService:
    def __init__(self, repo: MenuRepository) -> None:
        self.repo = repo

    def list_categories(self) -> list[CategoryOut]:
        return [
            CategoryOut.model_validate(c, from_attributes=True)
            for c in self.repo.list_active_categories()
        ]

    def get_category(self, category_id: uuid.UUID) -> CategoryOut:
        category = self.repo.get_active_category(category_id)
        if category is None:
            raise CategoryNotFoundError
        return CategoryOut.model_validate(category, from_attributes=True)

    def list_products(
        self,
        *,
        category_id: uuid.UUID | None,
        search: str | None,
        sort: ProductSort,
        page: int,
        page_size: int,
    ) -> tuple[list[ProductOut], Pagination]:
        rows, total = self.repo.search_visible(
            category_id=category_id,
            search=(search or "").strip() or None,
            sort=sort,
            page=page,
            page_size=page_size,
        )
        items = [_to_product_out(p, in_stock) for p, in_stock in rows]
        return items, build_pagination(page, page_size, total)

    def get_product(self, product_id: uuid.UUID) -> ProductOut:
        found = self.repo.get_visible(product_id)
        if found is None:
            raise ProductNotFoundError
        return _to_product_out(*found)
