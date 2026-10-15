from pydantic import BaseModel


class OrderCancelOut(BaseModel):
    order_number: str
    status: str
    # None = tidak ada uang yang perlu dikembalikan (order belum dibayar).
    refund_status: str | None
