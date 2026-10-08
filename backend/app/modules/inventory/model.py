import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.constraints import enum_check
from app.db.mixins import UUIDPrimaryKeyMixin


class StockMovementType(StrEnum):
    SALE = "SALE"
    RESERVATION = "RESERVATION"
    RELEASE = "RELEASE"
    RESTOCK = "RESTOCK"
    ADJUSTMENT = "ADJUSTMENT"
    WASTE = "WASTE"
    REMAKE = "REMAKE"


class Inventory(UUIDPrimaryKeyMixin, Base):
    """Stok level produk (MVP). Total fisik = available + reserved (tidak disimpan terpisah).

    Perubahan stok HARUS lewat UPDATE atomik bersyarat
    (... WHERE quantity_available >= :qty), bukan baca-lalu-tulis, dan selalu
    dicatat di stock_movements. CHECK >= 0 di bawah adalah jaring pengaman terakhir.
    """

    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("quantity_available >= 0", name="quantity_available_non_negative"),
        CheckConstraint("quantity_reserved >= 0", name="quantity_reserved_non_negative"),
        CheckConstraint("reorder_level >= 0", name="reorder_level_non_negative"),
    )

    # UNIQUE: satu produk = satu record inventory. RESTRICT: produk tidak dihapus fisik.
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="RESTRICT"), unique=True, nullable=False
    )
    quantity_available: Mapped[int] = mapped_column(
        Integer, server_default=text("0"), nullable=False
    )
    quantity_reserved: Mapped[int] = mapped_column(
        Integer, server_default=text("0"), nullable=False
    )
    reorder_level: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class StockMovement(UUIDPrimaryKeyMixin, Base):
    """Audit trail perubahan stok. Append-only: baris tidak diubah/dihapus.

    quantity = perubahan bertanda (+ menambah stok, - mengurangi). Tidak boleh 0.
    """

    __tablename__ = "stock_movements"
    __table_args__ = (
        CheckConstraint("quantity <> 0", name="quantity_non_zero"),
        CheckConstraint(enum_check("movement_type", StockMovementType), name="movement_type_valid"),
        Index("ix_stock_movements_product_created", "product_id", "created_at"),
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    movement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    # Referensi polimorfik (mis. order, reservation) -> sengaja tanpa FK.
    reference_type: Mapped[str | None] = mapped_column(String(50))
    reference_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    reason: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="RESTRICT")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ReservationStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CONVERTED = "CONVERTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class StockReservation(UUIDPrimaryKeyMixin, Base):
    """Stok yang ditahan sementara selama checkout/pembayaran.
    ACTIVE -> CONVERTED (dibayar) | EXPIRED (timeout) | CANCELLED (order batal)."""

    __tablename__ = "stock_reservations"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint(enum_check("status", ReservationStatus), name="status_valid"),
        # Worker kedaluwarsa mencari: status ACTIVE & expires_at lewat.
        Index("ix_stock_reservations_status_expires", "status", "expires_at"),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), server_default=ReservationStatus.ACTIVE.value, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
