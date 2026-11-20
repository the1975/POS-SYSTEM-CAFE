import uuid
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

MAX_QTY = 100000
# Jenis koreksi manual yang boleh dipilih admin (sama dengan frontend: STOCK_ACTIONS).
ManualType = Literal["RESTOCK", "ADJUSTMENT", "WASTE"]


class StockItemOut(BaseModel):
    product_id: uuid.UUID
    product_name: str
    category_name: str
    is_available: bool
    quantity_available: int
    quantity_reserved: int
    reorder_level: int


class StockAdjustIn(BaseModel):
    quantity: int = Field(description="Perubahan bertanda: + menambah, - mengurangi.")
    reason: str = Field(min_length=3, max_length=500)
    movement_type: ManualType

    @field_validator("reason")
    @classmethod
    def _strip_reason(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Alasan minimal 3 huruf.")
        return v

    @model_validator(mode="after")
    def _check_quantity(self):
        if self.quantity == 0 or abs(self.quantity) > MAX_QTY:
            raise ValueError("Jumlah harus 1 sampai 100000 (boleh negatif untuk mengurangi).")
        if self.movement_type == "RESTOCK" and self.quantity < 0:
            raise ValueError("Restock harus menambah stok.")
        if self.movement_type == "WASTE" and self.quantity > 0:
            raise ValueError("Barang rusak/terbuang harus mengurangi stok.")
        return self


class StockAdjustOut(BaseModel):
    product_id: uuid.UUID
    product_name: str
    quantity_available: int


class ReorderLevelIn(BaseModel):
    reorder_level: int = Field(ge=0, le=MAX_QTY, description="0 = tanpa peringatan.")


class ReorderLevelOut(BaseModel):
    product_id: uuid.UUID
    product_name: str
    reorder_level: int
