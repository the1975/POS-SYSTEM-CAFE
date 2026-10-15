import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PickupItemOut(BaseModel):
    name: str
    quantity: int


class PickupOrderOut(BaseModel):
    """Daftar untuk petugas pickup. Tanpa token apa pun dan tanpa data pembayaran."""

    pickup_id: uuid.UUID
    order_number: str
    customer_name: str
    status: str
    ready_at: datetime | None
    verified: bool
    items: list[PickupItemOut]


class PickupVerifyIn(BaseModel):
    pickup_token: str = Field(min_length=8, max_length=200)


class PickupVerifyOut(BaseModel):
    pickup_id: uuid.UUID  # dibutuhkan untuk langkah complete
    order_number: str
    customer_name: str
    status: str
    payment_status: str | None
    items: list[PickupItemOut]


class PickupCompleteOut(BaseModel):
    order_number: str
    status: str
    completed_at: datetime
