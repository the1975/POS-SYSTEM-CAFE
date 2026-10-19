"""Manajemen pengguna oleh ADMIN (api-design.md: User API). Otorisasi (hanya ADMIN) ada di
router; aturan bisnis dan audit log ada di sini."""

import uuid

from sqlalchemy.exc import IntegrityError

from app.core.responses import Pagination, build_pagination
from app.core.security import hash_password
from app.modules.audit.model import AuditLog
from app.modules.users.exceptions import (
    CannotModifySelfError,
    EmailAlreadyUsedError,
    LastAdminError,
    RoleNotFoundError,
    UserNotFoundError,
)
from app.modules.users.model import RoleName, User
from app.modules.users.repository import UserRepository
from app.modules.users.schema import RoleOut, UserCreateIn, UserItem, UserUpdateIn


def to_item(user: User) -> UserItem:
    return UserItem(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.name,
        role_id=user.role.id,
        is_active=user.is_active,
        created_at=user.created_at,
    )


class UserAdminService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    def list_users(
        self,
        *,
        role_id: uuid.UUID | None,
        is_active: bool | None,
        search: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[UserItem], Pagination]:
        users, total = self.repo.list_users(
            role_id=role_id, is_active=is_active, search=search, page=page, page_size=page_size
        )
        return [to_item(u) for u in users], build_pagination(page, page_size, total)

    def list_roles(self) -> list[RoleOut]:
        return [RoleOut(id=r.id, name=r.name) for r in self.repo.list_roles()]

    def create(self, data: UserCreateIn, admin: User) -> UserItem:
        role = self.repo.get_role(data.role_id)
        if role is None:
            raise RoleNotFoundError
        email = data.email.lower()
        if self.repo.get_by_email(email) is not None:
            raise EmailAlreadyUsedError
        user = User(
            role=role, name=data.name, email=email, password_hash=hash_password(data.password)
        )
        try:
            self.repo.add(user)
            self.repo.add(
                AuditLog(
                    user_id=admin.id,
                    action="CREATE_USER",
                    entity_type="user",
                    entity_id=user.id,
                    new_value={"name": user.name, "email": email, "role": role.name},
                )
            )
            self.repo.commit()
        except IntegrityError:
            self.repo.rollback()  # dua permintaan dengan email sama bersamaan: yang kedua kalah
            raise EmailAlreadyUsedError from None
        except Exception:
            self.repo.rollback()
            raise
        return to_item(user)

    def update(self, user_id: uuid.UUID, data: UserUpdateIn, admin: User) -> UserItem:
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError
        new_role = None
        if data.role_id is not None:
            new_role = self.repo.get_role(data.role_id)
            if new_role is None:
                raise RoleNotFoundError

        old = {"name": user.name, "role": user.role.name, "is_active": user.is_active}
        new = {
            "name": data.name if data.name is not None else user.name,
            "role": new_role.name if new_role else user.role.name,
            "is_active": data.is_active if data.is_active is not None else user.is_active,
        }
        if old == new:
            return to_item(user)  # tidak ada yang berubah: tidak perlu audit

        # Admin tidak boleh mengunci dirinya sendiri.
        if user.id == admin.id and (not new["is_active"] or new["role"] != old["role"]):
            raise CannotModifySelfError
        # Admin aktif terakhir tidak boleh hilang (dikunci supaya aman dari permintaan bersamaan).
        admin_name = RoleName.ADMIN.value
        was_admin = old["is_active"] and old["role"] == admin_name
        still_admin = new["is_active"] and new["role"] == admin_name
        if was_admin and not still_admin and self.repo.lock_active_admins() <= 1:
            self.repo.rollback()
            raise LastAdminError

        try:
            user.name = new["name"]
            user.is_active = new["is_active"]
            if new_role is not None:
                user.role = new_role
            self.repo.add(
                AuditLog(
                    user_id=admin.id,
                    action="UPDATE_USER",
                    entity_type="user",
                    entity_id=user.id,
                    old_value=old,
                    new_value=new,
                )
            )
            self.repo.commit()
        except Exception:
            self.repo.rollback()
            raise
        return to_item(user)
