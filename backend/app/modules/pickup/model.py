import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.constraints import enum_check
from app.db.mixins import UUIDPrimaryKeyMixin


class PickupStatus(StrEnum):
    WAITING_PICKUP = "WAITING_PICKUP"
    COMPLETED = "COMPLETED"


class Pickup(UUIDPrimaryKeyMixin, Base):
    """Satu order = satu pickup. Penyelesaian harus atomik: WAITING_PICKUP -> COMPLETED
    (UPDATE ... WHERE status = 'WAITING_PICKUP'), supaya dua staff tak bisa menyelesaikan
    order yang sama. Verifikasi dicatat via verified_by/verified_at (tanpa status VERIFIED)."""

    __tablename__ = "pickups"
    __table_args__ = (
        CheckConstraint(enum_check("status", PickupStatus), name="status_valid"),
        CheckConstraint(
            "status <> 'COMPLETED' OR completed_at IS NOT NULL", name="completed_has_timestamp"
        ),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("orders.id", ondelete="RESTRICT"), unique=True, nullable=False
    )
    # Hanya HASH token pickup yang disimpan.
    pickup_token_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), server_default=PickupStatus.WAITING_PICKUP.value, nullable=False
    )
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="RESTRICT")
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
