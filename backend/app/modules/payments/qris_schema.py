import uuid
from datetime import datetime

from pydantic import BaseModel


class QrisCreateIn(BaseModel):
    order_id: uuid.UUID


class QrisOut(BaseModel):
    payment_id: uuid.UUID
    payment_status: str
    payment_url: str
    expires_at: datetime | None
