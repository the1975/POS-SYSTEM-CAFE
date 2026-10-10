import uuid
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, field_serializer


class ProductSort(StrEnum):
    NAME = "name"  # default: urut kategori lalu nama (cocok untuk menu)
    PRICE_ASC = "price"
    PRICE_DESC = "-price"


class CategoryOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    sort_order: int


class ProductOut(BaseModel):
    """Bentuk produk untuk CUSTOMER. Sengaja tidak ada cost_price (HPP rahasia bisnis)."""

    id: uuid.UUID
    category_id: uuid.UUID
    name: str
    description: str | None
    price: Decimal
    image_url: str | None
    is_available: bool
    # Info tambahan agar UI bisa menampilkan "Habis". Hanya informasi, BUKAN jaminan stok:
    # validasi stok yang sebenarnya tetap di backend saat order dibuat.
    in_stock: bool

    @field_serializer("price", when_used="json")
    def _price_as_number(self, value: Decimal) -> int | float:
        # Rupiah biasanya bulat; JSON-nya angka (sesuai contoh api-design.md), bukan string.
        return int(value) if value == value.to_integral_value() else float(value)
