"""Pembatalan order oleh customer guest (dilindungi tracking token)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.responses import DataResponse
from app.db.dependencies import get_db
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.service import InventoryService
from app.modules.orders.cancel_schema import OrderCancelOut
from app.modules.orders.cancellation import OrderCancellationService
from app.modules.orders.repository import OrderRepository
from app.modules.payments.repository import PaymentRepository

router = APIRouter(prefix="/orders", tags=["orders"])


def get_cancellation_service(db: Annotated[Session, Depends(get_db)]) -> OrderCancellationService:
    inventory = InventoryService(
        InventoryRepository(db),
        reservation_timeout_minutes=get_settings().reservation_timeout_minutes,
    )
    return OrderCancellationService(OrderRepository(db), PaymentRepository(db), inventory)


@router.post("/{order_id}/cancel", response_model=DataResponse[OrderCancelOut])
def cancel_order(
    order_id: uuid.UUID,
    service: Annotated[OrderCancellationService, Depends(get_cancellation_service)],
    x_tracking_token: Annotated[str | None, Header()] = None,
):
    return DataResponse(data=service.cancel_by_customer(order_id, x_tracking_token))
