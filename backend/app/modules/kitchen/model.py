import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.constraints import enum_check
from app.db.mixins import UUIDPrimaryKeyMixin


class RemakeReason(StrEnum):
    WRONG_MENU = "WRONG_MENU"
    WRONG_SIZE = "WRONG_SIZE"
    WRONG_TOPPING = "WRONG_TOPPING"
    WRONG_QUANTITY = "WRONG_QUANTITY"
    DAMAGED_OR_SPILLED = "DAMAGED_OR_SPILLED"
    CUSTOMER_REQUEST = "CUSTOMER_REQUEST"
    OTHER = "OTHER"


class RemakeEvent(UUIDPrimaryKeyMixin, Base):
    """Remake memakai order_item_id yang SAMA (tidak membuat item/order baru)."""

    __tablename__ = "remake_events"
    __table_args__ = (CheckConstraint(enum_check("reason", RemakeReason), name="reason_valid"),)

    order_item_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("order_items.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    reason: Mapped[str] = mapped_column(String(30), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
