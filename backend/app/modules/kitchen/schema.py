import uuid
from datetime import datetime

from pydantic import BaseModel


class KitchenItemOut(BaseModel):
    order_item_id: uuid.UUID
    name: str
    quantity: int
    status: str


class KitchenOrderOut(BaseModel):
    """Tampilan order untuk dapur. Tanpa data pembayaran dan tanpa token apa pun."""

    order_id: uuid.UUID
    order_number: str
    customer_name: str
    status: str
    confirmed_at: datetime | None
    preparing_at: datetime | None
    ready_at: datetime | None
    items: list[KitchenItemOut]
