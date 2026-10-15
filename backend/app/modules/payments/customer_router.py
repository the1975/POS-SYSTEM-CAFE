"""Endpoint pembayaran tanpa login: customer (dilindungi tracking token) dan webhook provider
(dilindungi tanda tangan)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.responses import DataResponse
from app.db.dependencies import get_db
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.service import InventoryService
from app.modules.orders.repository import OrderRepository
from app.modules.payments.provider import PaymentProvider
from app.modules.payments.provider_factory import get_payment_provider
from app.modules.payments.qris_schema import QrisCreateIn, QrisOut
from app.modules.payments.qris_service import QrisService
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.webhook_schema import WebhookOut
from app.modules.payments.webhook_service import WebhookService

router = APIRouter(prefix="/payments", tags=["payments"])

ProviderDep = Annotated[PaymentProvider, Depends(get_payment_provider)]
DbDep = Annotated[Session, Depends(get_db)]


def get_qris_service(db: DbDep, provider: ProviderDep) -> QrisService:
    return QrisService(PaymentRepository(db), OrderRepository(db), provider)


def get_webhook_service(db: DbDep, provider: ProviderDep) -> WebhookService:
    inventory = InventoryService(
        InventoryRepository(db),
        reservation_timeout_minutes=get_settings().reservation_timeout_minutes,
    )
    return WebhookService(PaymentRepository(db), OrderRepository(db), inventory, provider)


async def _raw_body(request: Request) -> bytes:
    # Tanda tangan dihitung dari body MENTAH; harus dibaca sebelum di-parse.
    return await request.body()


@router.post("/qris", response_model=DataResponse[QrisOut])
def create_qris_payment(
    body: QrisCreateIn,
    service: Annotated[QrisService, Depends(get_qris_service)],
    x_tracking_token: Annotated[str | None, Header()] = None,
):
    return DataResponse(data=service.create_for_order(body.order_id, x_tracking_token))


@router.post("/webhook", response_model=DataResponse[WebhookOut])
def payment_webhook(
    raw_body: Annotated[bytes, Depends(_raw_body)],
    service: Annotated[WebhookService, Depends(get_webhook_service)],
    x_signature: Annotated[str | None, Header()] = None,
):
    return DataResponse(data=service.handle(raw_body, x_signature))
