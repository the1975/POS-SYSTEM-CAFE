"""Bentuk data untuk ADMIN mengelola produk. Beda dengan ProductOut (customer):
di sini cost_price (HPP) BOLEH tampil karena endpoint-nya hanya untuk ADMIN."""

import uuid
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, field_serializer, field_validator, model_validator

# Rupiah: NUMERIC(12,2) di database, jadi dibatasi sama di sini. ge=0 = tidak boleh negatif.
Money = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
Name = Annotated[str, Field(min_length=1, max_length=150)]


def _blank_to_none(value: str | None) -> str | None:
    """Spasi di pinggir dibuang; teks kosong dianggap 'tidak ada isi' (disimpan NULL)."""
    if value is None:
        return None
    value = value.strip()
    return value or None


class ProductCreateIn(BaseModel):
    category_id: uuid.UUID
    name: Name
    description: str | None = Field(default=None, max_length=1000)
    price: Money
    cost_price: Money
    image_url: str | None = Field(default=None, max_length=500)
    is_available: bool = True

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Nama produk tidak boleh kosong")
        return v

    @field_validator("description", "image_url")
    @classmethod
    def _clean_optional(cls, v: str | None) -> str | None:
        return _blank_to_none(v)


class ProductUpdateIn(BaseModel):
    """PATCH: hanya field yang DIKIRIM yang diubah. description/image_url boleh dikirim
    null untuk mengosongkan; field lain tidak boleh null."""

    category_id: uuid.UUID | None = None
    name: Name | None = None
    description: str | None = Field(default=None, max_length=1000)
    price: Money | None = None
    cost_price: Money | None = None
    image_url: str | None = Field(default=None, max_length=500)
    is_available: bool | None = None

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Nama produk tidak boleh kosong")
        return v

    @field_validator("description", "image_url")
    @classmethod
    def _clean_optional(cls, v: str | None) -> str | None:
        return _blank_to_none(v)

    @model_validator(mode="after")
    def _check_fields(self):
        sent = self.model_fields_set
        if not sent:
            raise ValueError("Isi minimal satu field yang mau diubah")
        # Field wajib tidak boleh dikirim null (null hanya sah untuk mengosongkan teks opsional).
        required = {"category_id", "name", "price", "cost_price", "is_available"}
        for field in required & sent:
            if getattr(self, field) is None:
                raise ValueError(f"{field} tidak boleh null")
        return self


class ProductAdminOut(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID
    name: str
    description: str | None
    price: Decimal
    cost_price: Decimal
    image_url: str | None
    is_available: bool

    @field_serializer("price", "cost_price", when_used="json")
    def _money_as_number(self, value: Decimal) -> int | float:
        # Rupiah biasanya bulat; JSON-nya angka (sama seperti ProductOut).
        return int(value) if value == value.to_integral_value() else float(value)
