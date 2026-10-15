"""Endpoint dapur (wajib login). OWNER di spec = ADMIN di kode."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.responses import DataResponse, PageResponse
from app.db.dependencies import get_db
from app.modules.kitchen.remake_schema import RemakeIn, to_db_reason
from app.modules.kitchen.repository import KitchenRepository
from app.modules.kitchen.schema import KitchenOrderOut
from app.modules.kitchen.service import KitchenService
from app.modules.orders.model import OrderStatus
from app.modules.orders.repository import OrderRepository
from app.modules.pickup.repository import PickupRepository
from app.modules.users.dependencies import require_roles
from app.modules.users.model import RoleName, User

router = APIRouter(prefix="/kitchen", tags=["kitchen"])

KitchenUser = Annotated[
    User, Depends(require_roles(RoleName.KITCHEN, RoleName.CONTROLLER, RoleName.ADMIN))
]


def get_kitchen_service(db: Annotated[Session, Depends(get_db)]) -> KitchenService:
    return KitchenService(KitchenRepository(db), OrderRepository(db), PickupRepository(db))


ServiceDep = Annotated[KitchenService, Depends(get_kitchen_service)]


@router.get("/orders", response_model=PageResponse[KitchenOrderOut])
def list_kitchen_orders(
    service: ServiceDep,
    user: KitchenUser,
    status: OrderStatus | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    items, pagination = service.list_orders(status=status, page=page, page_size=page_size)
    return PageResponse(data=items, pagination=pagination)


@router.post("/orders/{order_id}/start", response_model=DataResponse[KitchenOrderOut])
def start_order(order_id: uuid.UUID, service: ServiceDep, user: KitchenUser):
    return DataResponse(data=service.start_order(order_id, user.id))


@router.post("/order-items/{order_item_id}/ready", response_model=DataResponse[KitchenOrderOut])
def mark_item_ready(order_item_id: uuid.UUID, service: ServiceDep, user: KitchenUser):
    return DataResponse(data=service.mark_item_ready(order_item_id, user.id))


@router.post("/order-items/{order_item_id}/remake", response_model=DataResponse[KitchenOrderOut])
def remake_item(order_item_id: uuid.UUID, body: RemakeIn, service: ServiceDep, user: KitchenUser):
    reason = to_db_reason(body.reason)
    return DataResponse(data=service.request_remake(order_item_id, reason, body.notes, user.id))
