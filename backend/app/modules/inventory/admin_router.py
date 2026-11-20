"""Endpoint stok untuk ADMIN: daftar stok dan koreksi manual."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.responses import DataResponse, PageResponse
from app.db.dependencies import get_db
from app.modules.inventory.admin_repository import InventoryAdminRepository
from app.modules.inventory.admin_schema import StockAdjustIn, StockAdjustOut, StockItemOut
from app.modules.inventory.admin_service import InventoryAdminService
from app.modules.users.dependencies import require_roles
from app.modules.users.model import RoleName, User

router = APIRouter(prefix="/inventory", tags=["inventory-admin"])

AdminUser = Annotated[User, Depends(require_roles(RoleName.ADMIN))]


def get_inventory_admin_service(db: Annotated[Session, Depends(get_db)]) -> InventoryAdminService:
    return InventoryAdminService(InventoryAdminRepository(db))


ServiceDep = Annotated[InventoryAdminService, Depends(get_inventory_admin_service)]


@router.get("", response_model=PageResponse[StockItemOut])
def list_stock(
    service: ServiceDep,
    admin: AdminUser,
    category_id: uuid.UUID | None = None,
    search: Annotated[str | None, Query(max_length=100)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    items, pagination = service.list_stock(
        category_id=category_id, search=search, page=page, page_size=page_size
    )
    return PageResponse(data=items, pagination=pagination)


@router.post("/{product_id}/adjust", response_model=DataResponse[StockAdjustOut])
def adjust_stock(product_id: uuid.UUID, body: StockAdjustIn, service: ServiceDep, admin: AdminUser):
    return DataResponse(data=service.adjust(product_id, body, admin))
