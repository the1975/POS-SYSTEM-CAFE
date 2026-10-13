"""Endpoint order untuk customer guest (tanpa login)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response

from app.core.responses import DataResponse
from app.modules.orders.dependencies import get_order_service
from app.modules.orders.schema import CreateOrderIn, OrderCreatedOut, OrderDetailOut
from app.modules.orders.service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])
ServiceDep = Annotated[OrderService, Depends(get_order_service)]


@router.post("", status_code=201, response_model=DataResponse[OrderCreatedOut])
def create_order(
    body: CreateOrderIn,
    service: ServiceDep,
    response: Response,
    # Wajib: mencegah order ganda saat double-click / retry jaringan.
    idempotency_key: Annotated[str, Header(min_length=8, max_length=100)],
):
    order, replayed = service.create_order(body, idempotency_key)
    if replayed:
        response.status_code = 200  # bukan order baru; isinya order yang sama
    return DataResponse(data=order)


@router.get("/{order_id}", response_model=DataResponse[OrderDetailOut])
def get_order(
    order_id: uuid.UUID,
    service: ServiceDep,
    # Token dikirim lewat header (bukan URL) agar tidak tersimpan di log/riwayat browser.
    x_tracking_token: Annotated[str | None, Header()] = None,
):
    return DataResponse(data=service.get_order_for_customer(order_id, x_tracking_token))
