import uuid
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.modules.orders.schema import Money


class CashConfirmIn(BaseModel):
    # Hanya uang yang diterima. Kembalian TIDAK diterima dari client (dihitung backend).
    cash_received: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class CashConfirmOut(BaseModel):
    payment_id: uuid.UUID
    payment_status: str
    order_status: str
    amount: Money
    cash_received: Money
    change: Money


class RefundIn(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    reason: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=500)]


class RefundOut(BaseModel):
    payment_id: uuid.UUID
    payment_status: str
    order_status: str
    refunded_amount: Money
