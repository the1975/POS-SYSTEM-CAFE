"""Akses database user. Hanya query; aturan login ada di AuthService."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.users.model import Role, RoleName, User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(func.lower(User.email) == email.strip().lower())
        return self.db.scalar(stmt)

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    # ---- Manajemen pengguna (admin) ----
    def list_users(
        self,
        *,
        role_id: uuid.UUID | None,
        is_active: bool | None,
        search: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[User], int]:
        filters = []
        if role_id is not None:
            filters.append(User.role_id == role_id)
        if is_active is not None:
            filters.append(User.is_active.is_(is_active))
        if search:
            # autoescape: karakter % dan _ dari user dianggap teks biasa, bukan wildcard.
            filters.append(
                User.name.icontains(search, autoescape=True)
                | User.email.icontains(search, autoescape=True)
            )
        total = self.db.scalar(select(func.count()).select_from(User).where(*filters)) or 0
        stmt = (
            select(User)
            .where(*filters)
            .order_by(User.name, User.id)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        return list(self.db.scalars(stmt)), total

    def list_roles(self) -> list[Role]:
        return list(self.db.scalars(select(Role).order_by(Role.name)))

    def get_role(self, role_id: uuid.UUID) -> Role | None:
        return self.db.get(Role, role_id)

    def lock_active_admins(self) -> int:
        """Kunci baris admin aktif (cegah dua admin saling menghapus bersamaan), lalu hitung."""
        stmt = (
            select(User.id)
            .join(Role, User.role_id == Role.id)
            .where(Role.name == RoleName.ADMIN.value, User.is_active.is_(True))
            .with_for_update(of=User)
        )
        return len(self.db.execute(stmt).all())

    def add(self, *objects) -> None:
        self.db.add_all(objects)
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
