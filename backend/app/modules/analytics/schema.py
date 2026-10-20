"""Bentuk response laporan (api-design.md: Analytics API)."""

import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, field_serializer


def _money(value: Decimal) -> int | float:
    # Rupiah biasanya bulat; JSON-nya angka (sama seperti endpoint produk).
    return int(value) if value == value.to_integral_value() else float(value)


class SummaryOut(BaseModel):
    start_date: date
    end_date: date
    revenue: Decimal
    orders: int
    units_sold: int
    average_order_value: Decimal

    @field_serializer("revenue", "average_order_value", when_used="json")
    def _as_number(self, value: Decimal) -> int | float:
        return _money(value)


class TopProductOut(BaseModel):
    product_id: uuid.UUID
    product_name: str
    units_sold: int
    revenue: Decimal

    @field_serializer("revenue", when_used="json")
    def _as_number(self, value: Decimal) -> int | float:
        return _money(value)


class PeakHourOut(BaseModel):
    hour: int  # 0-23, jam WIB
    orders: int
