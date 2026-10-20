"""Endpoint kelola produk. Hanya ADMIN (di kode OWNER = ADMIN).
Sengaja TIDAK ada DELETE: produk disembunyikan lewat PATCH is_available=false."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.responses import DataResponse
from app.db.dependencies import get_db
from app.modules.products.admin_repository import ProductAdminRepository
from app.modules.products.admin_schema import ProductAdminOut, ProductCreateIn, ProductUpdateIn
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
