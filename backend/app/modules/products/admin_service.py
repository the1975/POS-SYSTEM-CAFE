"""Pengelolaan produk oleh ADMIN (api-design.md: POST/PATCH /products).

Aturan penting:
- Produk TIDAK dihapus fisik. "Menghapus" = PATCH is_available=false (hilang dari menu customer).
- Ubah harga tidak menyentuh order lama: order memakai snapshot (unit_price) sendiri.
- Setiap perubahan dicatat di audit_logs (siapa, apa, nilai lama -> baru).
"""

import uuid
from decimal import Decimal

from app.core.responses import Pagination, build_pagination

from app.modules.audit.model import AuditLog
from app.modules.products.admin_repository import ProductAdminRepository
from app.modules.products.admin_schema import (
    ProductAdminListItem,
    ProductAdminOut,
    ProductCreateIn,
    ProductUpdateIn,
)
from app.modules.products.exceptions import InvalidCategoryError, ProductNotFoundError
from app.modules.products.model import Product
from app.modules.users.model import User


def to_admin_out(product: Product) -> ProductAdminOut:
    return ProductAdminOut(
        id=product.id,
        category_id=product.category_id,
        name=product.name,
        description=product.description,
        price=product.price,
        cost_price=product.cost_price,
        image_url=product.image_url,
        is_available=product.is_available,
    )


def _audit_value(value):
    """JSONB tidak mengerti Decimal/UUID, jadi diubah ke angka/teks biasa."""
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    return value


class ProductAdminService:
    def __init__(self, repo: ProductAdminRepository) -> None:
        self.repo = repo

    def list_products(
        self,
        *,
        category_id: uuid.UUID | None,
        is_available: bool | None,
        search: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ProductAdminListItem], Pagination]:
        rows, total = self.repo.list_for_admin(
            category_id=category_id,
            is_available=is_available,
            search=(search or "").strip() or None,
            page=page,
            page_size=page_size,
        )
        items = [
            ProductAdminListItem(**to_admin_out(p).model_dump(), category_name=cat_name)
            for p, cat_name in rows
        ]
        return items, build_pagination(page, page_size, total)

    def create(self, data: ProductCreateIn, admin: User) -> ProductAdminOut:
        if self.repo.get_category(data.category_id) is None:
            raise InvalidCategoryError
        product = Product(**data.model_dump())
        try:
            self.repo.add(product)
            self.repo.add(
                AuditLog(
                    user_id=admin.id,
                    action="CREATE_PRODUCT",
                    entity_type="product",
                    entity_id=product.id,
                    new_value={k: _audit_value(v) for k, v in data.model_dump().items()},
                )
            )
            self.repo.commit()
        except Exception:
            self.repo.rollback()
            raise
        return to_admin_out(product)

    def update(self, product_id: uuid.UUID, data: ProductUpdateIn, admin: User) -> ProductAdminOut:
        product = self.repo.get_product(product_id)
        if product is None:
            raise ProductNotFoundError

        changes = data.model_dump(exclude_unset=True)  # hanya field yang dikirim
        if "category_id" in changes and self.repo.get_category(changes["category_id"]) is None:
            raise InvalidCategoryError

        # Catat hanya field yang BENAR-BENAR berubah (nilai lama -> baru).
        old: dict = {}
        new: dict = {}
        for field, value in changes.items():
            current = getattr(product, field)
            if current != value:
                old[field] = _audit_value(current)
                new[field] = _audit_value(value)
        if not new:
            return to_admin_out(product)  # tidak ada yang berubah: tidak perlu audit

        try:
            for field in new:
                setattr(product, field, changes[field])
            self.repo.add(
                AuditLog(
                    user_id=admin.id,
                    # Perubahan harga diberi nama sendiri supaya gampang dicari saat audit.
                    action="UPDATE_PRODUCT_PRICE" if "price" in new else "UPDATE_PRODUCT",
                    entity_type="product",
                    entity_id=product.id,
                    old_value=old,
                    new_value=new,
                )
            )
            self.repo.commit()
        except Exception:
            self.repo.rollback()
            raise
        return to_admin_out(product)
