"""Daftar order untuk staff (wajib login; semua role staff boleh melihat)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.responses import PageResponse
from app.db.dependencies import get_db
from app.modules.orders.model import OrderStatus
from app.modules.orders.staff_repository import StaffOrderRepository
from app.modules.orders.staff_schema import StaffOrderOut
from app.modules.orders.staff_service import StaffOrderService
from app.modules.payments.model import PaymentStatus
from app.modules.users.dependencies import require_roles
from app.modules.users.model import RoleName

router = APIRouter(
    prefix="/staff/orders",
    tags=["staff-orders"],
    dependencies=[Depends(require_roles(*RoleName))],
)


def get_staff_order_service(db: Annotated[Session, Depends(get_db)]) -> StaffOrderService:
    return StaffOrderService(StaffOrderRepository(db))


@router.get("", response_model=PageResponse[StaffOrderOut])
def list_staff_orders(
    service: Annotated[StaffOrderService, Depends(get_staff_order_service)],
    status: OrderStatus | None = None,
    payment_status: PaymentStatus | None = None,
    search: Annotated[str | None, Query(max_length=100)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    items, pagination = service.list_orders(
        status=status,
        payment_status=payment_status,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PageResponse(data=items, pagination=pagination)
