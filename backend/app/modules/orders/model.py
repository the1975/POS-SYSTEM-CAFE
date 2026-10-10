import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.constraints import enum_check
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY = "READY"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    OVERDUE = "OVERDUE"  # dari READY, bukan otomatis batal


class PaymentMethod(StrEnum):
    QRIS = "QRIS"
    CASH = "CASH"


class OrderItemStatus(StrEnum):
    PENDING = "PENDING"
    PREPARING = "PREPARING"
    READY = "READY"
    REMAKE = "REMAKE"


class Order(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Transaksi customer. id = identitas internal; order_number = untuk manusia (bukan secret).
    Posisi antrean TIDAK disimpan (diturunkan dari state operasional)."""

    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="subtotal_non_negative"),
        CheckConstraint("discount_amount >= 0", name="discount_non_negative"),
        CheckConstraint("tax_amount >= 0", name="tax_non_negative"),
        CheckConstraint("total >= 0", name="total_non_negative"),
        # Diskon tidak boleh melebihi nilai transaksi yang eligible.
        CheckConstraint("discount_amount <= subtotal", name="discount_within_subtotal"),
        CheckConstraint(enum_check("status", OrderStatus), name="status_valid"),
        CheckConstraint(enum_check("payment_method", PaymentMethod), name="payment_method_valid"),
        Index("ix_orders_created_at", "created_at"),
    )

    order_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    # Nama hanya untuk dibaca manusia, bukan identitas/kredensial.
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Kunci idempotensi dari client (header Idempotency-Key): mencegah order ganda saat
    # double-click / retry jaringan. NULL untuk order yang tidak dibuat lewat checkout.
    idempotency_key: Mapped[str | None] = mapped_column(String(100), unique=True)
    # Hanya HASH token yang disimpan; token asli cuma dipegang customer.
    tracking_token_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), server_default=OrderStatus.PENDING.value, nullable=False, index=True
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), server_default=text("0"), nullable=False
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), server_default=text("0"), nullable=False
    )
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(10), nullable=False)

    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    preparing_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", order_by="OrderItem.created_at"
    )


class OrderItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Item order dengan SNAPSHOT nama & harga: histori tidak berubah saat produk diubah."""

    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price >= 0", name="unit_price_non_negative"),
        CheckConstraint("subtotal >= 0", name="subtotal_non_negative"),
        CheckConstraint(enum_check("status", OrderItemStatus), name="status_valid"),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    product_name_snapshot: Mapped[str] = mapped_column(String(150), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), server_default=OrderItemStatus.PENDING.value, nullable=False
    )

    order: Mapped[Order] = relationship(back_populates="items")
