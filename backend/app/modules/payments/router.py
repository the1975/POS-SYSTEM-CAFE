"""Endpoint pembayaran untuk staff (wajib login)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.responses import DataResponse
from app.modules.payments.dependencies import get_payment_service
from app.modules.payments.schema import CashConfirmIn, CashConfirmOut
from app.modules.payments.service import PaymentService
from app.modules.users.dependencies import require_roles
from app.modules.users.model import RoleName, User

router = APIRouter(prefix="/payments", tags=["payments"])

# OWNER di spec = ADMIN di kode.
CashierUser = Annotated[User, Depends(require_roles(RoleName.CASHIER, RoleName.ADMIN))]
ServiceDep = Annotated[PaymentService, Depends(get_payment_service)]


@router.post("/{payment_id}/cash-confirm", response_model=DataResponse[CashConfirmOut])
def confirm_cash(
    payment_id: uuid.UUID, body: CashConfirmIn, service: ServiceDep, user: CashierUser
):
    return DataResponse(data=service.confirm_cash(payment_id, body.cash_received, user.id))
