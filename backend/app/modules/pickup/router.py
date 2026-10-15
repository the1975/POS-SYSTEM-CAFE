"""Endpoint pickup (wajib login). OWNER di spec = ADMIN di kode."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.responses import DataResponse, PageResponse
from app.db.dependencies import get_db
from app.modules.orders.model import OrderStatus
from app.modules.orders.repository import OrderRepository
from app.modules.pickup.repository import PickupRepository
from app.modules.pickup.schema import (
    PickupCompleteOut,
    PickupOrderOut,
    PickupVerifyIn,
    PickupVerifyOut,
)
from app.modules.pickup.service import PickupService
from app.modules.users.dependencies import require_roles
from app.modules.users.model import RoleName, User

router = APIRouter(prefix="/pickup", tags=["pickup"])

PickupUser = Annotated[
    User, Depends(require_roles(RoleName.PICKUP, RoleName.CONTROLLER, RoleName.ADMIN))
]


def get_pickup_service(db: Annotated[Session, Depends(get_db)]) -> PickupService:
    return PickupService(PickupRepository(db), OrderRepository(db))


ServiceDep = Annotated[PickupService, Depends(get_pickup_service)]


@router.get("/orders", response_model=PageResponse[PickupOrderOut])
def list_pickup_orders(
    service: ServiceDep,
    user: PickupUser,
    status: OrderStatus = OrderStatus.READY,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    items, pagination = service.list_orders(status=status, page=page, page_size=page_size)
    return PageResponse(data=items, pagination=pagination)


@router.post("/verify", response_model=DataResponse[PickupVerifyOut])
def verify_pickup(body: PickupVerifyIn, service: ServiceDep, user: PickupUser):
    return DataResponse(data=service.verify(body.pickup_token, user.id))


@router.post("/{pickup_id}/complete", response_model=DataResponse[PickupCompleteOut])
def complete_pickup(pickup_id: uuid.UUID, service: ServiceDep, user: PickupUser):
    return DataResponse(data=service.complete(pickup_id, user.id))
