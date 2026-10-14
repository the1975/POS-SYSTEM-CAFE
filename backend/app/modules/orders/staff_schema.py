import uuid
from datetime import datetime

from pydantic import BaseModel

from app.modules.orders.schema import Money


class StaffOrderOut(BaseModel):
    """Ringkasan order untuk staff. payment_id dipakai kasir untuk cash-confirm.
    Tidak ada token tracking/pickup di sini."""

    order_id: uuid.UUID
    order_number: str
    customer_name: str
    status: str
    payment_id: uuid.UUID | None
    payment_method: str
    payment_status: str | None
    total: Money
    created_at: datetime
