from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from app.modules.kitchen.model import RemakeReason


class RemakeReasonIn(StrEnum):
    """Alasan yang diterima API. Spec memisahkan DAMAGED dan SPILLED, sedangkan tabel
    remake_events hanya punya DAMAGED_OR_SPILLED: keduanya diterima lalu digabung."""

    WRONG_MENU = "WRONG_MENU"
    WRONG_SIZE = "WRONG_SIZE"
    WRONG_TOPPING = "WRONG_TOPPING"
    WRONG_QUANTITY = "WRONG_QUANTITY"
    DAMAGED = "DAMAGED"
    SPILLED = "SPILLED"
    DAMAGED_OR_SPILLED = "DAMAGED_OR_SPILLED"
    CUSTOMER_REQUEST = "CUSTOMER_REQUEST"
    OTHER = "OTHER"


_TO_DB = {
    RemakeReasonIn.DAMAGED: RemakeReason.DAMAGED_OR_SPILLED,
    RemakeReasonIn.SPILLED: RemakeReason.DAMAGED_OR_SPILLED,
}


def to_db_reason(reason: RemakeReasonIn) -> RemakeReason:
    return _TO_DB.get(reason) or RemakeReason(reason.value)


class RemakeIn(BaseModel):
    reason: RemakeReasonIn
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("notes")
    @classmethod
    def _clean_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None  # catatan kosong/spasi saja dianggap tidak ada
