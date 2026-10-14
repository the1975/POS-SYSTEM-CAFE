import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class CashConfirmIn(BaseModel):
    # Hanya uang yang diterima. Kembalian TIDAK diterima dari client (dihitung backend).
    cash_received: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class CashConfirmOut(BaseModel):
    payment_id: uuid.UUID
    payment_status: str
    order_status: str
    amount: Decimal
    cash_received: Decimal
    change: Decimal
