import uuid
from enum import StrEnum

from sqlalchemy import Boolean, ForeignKey, String, Text, Uuid, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class RoleName(StrEnum):
    ADMIN = "ADMIN"
    CONTROLLER = "CONTROLLER"
    KITCHEN = "KITCHEN"
    CASHIER = "CASHIER"
    PICKUP = "PICKUP"


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Hanya staff/admin. Customer guest tidak punya akun."""

    __tablename__ = "users"

    # RESTRICT: role yang masih dipakai tidak boleh terhapus.
    role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    # Akun nonaktif, bukan dihapus: riwayat tetap menyimpan user_id.
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true(), nullable=False)

    role: Mapped[Role] = relationship(lazy="joined")
