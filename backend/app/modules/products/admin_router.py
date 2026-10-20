"""Endpoint kelola produk. Hanya ADMIN (di kode OWNER = ADMIN).
Sengaja TIDAK ada DELETE: produk disembunyikan lewat PATCH is_available=false."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.responses import DataResponse, PageResponse
from app.db.dependencies import get_db
from app.modules.products.admin_repository import ProductAdminRepository
from app.modules.products.admin_schema import (
    ProductAdminListItem,
    ProductAdminOut,
    ProductCreateIn,
    ProductUpdateIn,
)
from app.modules.products.admin_service import ProductAdminService
from app.modules.users.dependencies import require_roles
from app.modules.users.model import RoleName, User

router = APIRouter(prefix="/products", tags=["products-admin"])

AdminUser = Annotated[User, Depends(require_roles(RoleName.ADMIN))]


def get_product_admin_service(db: Annotated[Session, Depends(get_db)]) -> ProductAdminService:
    return ProductAdminService(ProductAdminRepository(db))


ServiceDep = Annotated[ProductAdminService, Depends(get_product_admin_service)]


@router.post("", status_code=201, response_model=DataResponse[ProductAdminOut])
def create_product(body: ProductCreateIn, service: ServiceDep, admin: AdminUser):
    return DataResponse(data=service.create(body, admin))


@router.patch("/{product_id}", response_model=DataResponse[ProductAdminOut])
def update_product(
    product_id: uuid.UUID, body: ProductUpdateIn, service: ServiceDep, admin: AdminUser
):
    return DataResponse(data=service.update(product_id, body, admin))


# Prefix terpisah: GET /products/{apa-saja} sudah dipakai menu customer (bentrok kalau disamakan).
list_router = APIRouter(prefix="/admin/products", tags=["products-admin"])


@list_router.get("", response_model=PageResponse[ProductAdminListItem])
def list_products_admin(
    service: ServiceDep,
    admin: AdminUser,
    category_id: uuid.UUID | None = None,
    is_available: bool | None = None,  # kosong = semua (tampil + disembunyikan)
    search: Annotated[str | None, Query(max_length=100)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    items, pagination = service.list_products(
        category_id=category_id,
        is_available=is_available,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PageResponse(data=items, pagination=pagination)
