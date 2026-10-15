"""Endpoint pembayaran untuk customer guest (tanpa login; dilindungi tracking token)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.responses import DataResponse
from app.db.dependencies import get_db
from app.modules.orders.repository import OrderRepository
from app.modules.payments.mock_provider import MockQrisProvider
from app.modules.payments.qris_schema import QrisCreateIn, QrisOut
from app.modules.payments.qris_service import QrisService
from app.modules.payments.repository import PaymentRepository

router = APIRouter(prefix="/payments", tags=["payments"])


def get_qris_service(db: Annotated[Session, Depends(get_db)]) -> QrisService:
    # Ganti MockQrisProvider ke provider asli di sini saat sudah diputuskan.
    return QrisService(PaymentRepository(db), OrderRepository(db), MockQrisProvider())


@router.post("/qris", response_model=DataResponse[QrisOut])
def create_qris_payment(
    body: QrisCreateIn,
    service: Annotated[QrisService, Depends(get_qris_service)],
    x_tracking_token: Annotated[str | None, Header()] = None,
):
    return DataResponse(data=service.create_for_order(body.order_id, x_tracking_token))
