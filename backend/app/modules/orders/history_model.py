import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.constraints import enum_check
from app.db.mixins import UUIDPrimaryKeyMixin
from app.modules.orders.model import OrderStatus


class OrderStatusHistory(UUIDPrimaryKeyMixin, Base):
    """Jejak setiap perubahan status order. Append-only."""

    __tablename__ = "order_status_history"
    __table_args__ = (
        CheckConstraint(enum_check("to_status", OrderStatus), name="to_status_valid"),
        CheckConstraint(
            f"from_status IS NULL OR {enum_check('from_status', OrderStatus)}",
            name="from_status_valid",
        ),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    # NULL pada entri pertama (order baru dibuat).
    from_status: Mapped[str | None] = mapped_column(String(20))
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    # NULL = perubahan oleh sistem/webhook/customer guest.
    changed_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="RESTRICT")
    )
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
