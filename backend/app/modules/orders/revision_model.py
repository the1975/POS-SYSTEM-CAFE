import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import UUIDPrimaryKeyMixin


class OrderRevision(UUIDPrimaryKeyMixin, Base):
    """Snapshot order tiap kali diedit. Order tetap sama (order_id tidak berubah);
    revisi lama tidak pernah ditimpa. Urutan revision_number dijaga service."""

    __tablename__ = "order_revisions"
    __table_args__ = (
        UniqueConstraint("order_id", "revision_number", name="order_revision_number"),
        CheckConstraint("revision_number >= 1", name="revision_number_positive"),
        CheckConstraint("subtotal >= 0", name="subtotal_non_negative"),
        CheckConstraint("discount_amount >= 0", name="discount_non_negative"),
        CheckConstraint("tax_amount >= 0", name="tax_non_negative"),
        CheckConstraint("total >= 0", name="total_non_negative"),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    # NULL = diubah customer guest; terisi jika staff yang mengubah.
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class OrderRevisionItem(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "order_revision_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price >= 0", name="unit_price_non_negative"),
        CheckConstraint("subtotal >= 0", name="subtotal_non_negative"),
    )

    order_revision_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("order_revisions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    product_name_snapshot: Mapped[str] = mapped_column(String(150), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
