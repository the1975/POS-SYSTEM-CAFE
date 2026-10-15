import uuid
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

from app.modules.orders.model import PaymentMethod


def _as_json_number(value: Decimal) -> int | float:
    # Rupiah biasanya bulat; di JSON jadi angka (bukan string), sesuai api-design.md.
    return int(value) if value == value.to_integral_value() else float(value)


Money = Annotated[Decimal, PlainSerializer(_as_json_number, when_used="json")]


class OrderItemIn(BaseModel):
    # forbid: field tak dikenal (mis. "price" / "total" dari client) ditolak, bukan diam-diam diabaikan.
    model_config = ConfigDict(extra="forbid")

    product_id: uuid.UUID
    quantity: int = Field(ge=1)  # batas atas dicek service (bisa diatur lewat konfigurasi)


class CreateOrderIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    customer_name: str = Field(min_length=1, max_length=100)
    items: list[OrderItemIn] = Field(min_length=1, max_length=50)
    payment_method: PaymentMethod


class OrderCreatedOut(BaseModel):
    order_id: uuid.UUID
    order_number: str
    customer_name: str
    status: str
    payment_method: str
    subtotal: Money
    discount_amount: Money
    tax_amount: Money
    total: Money
    # Token mentah hanya diberikan sekali (saat dibuat / saat request ulang idempotent).
    tracking_token: str


class OrderItemOut(BaseModel):
    name: str
    quantity: int
    status: str


class OrderDetailOut(BaseModel):
    order_id: uuid.UUID
    order_number: str
    customer_name: str
    status: str
    payment_method: str
    payment_status: str | None
    pickup_token: str | None
    items: list[OrderItemOut]
    subtotal: Money
    discount_amount: Money
    tax_amount: Money
    total: Money
