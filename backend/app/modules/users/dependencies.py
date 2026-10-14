"""Penjaga endpoint staff: siapa yang login (get_current_user) dan apakah role-nya boleh
(require_roles). Otorisasi SELALU di backend; frontend hanya menyembunyikan tombol."""

import uuid
from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.dependencies import get_db
from app.modules.users.exceptions import ForbiddenError, UnauthorizedError
from app.modules.users.model import RoleName, User
from app.modules.users.repository import UserRepository
from app.modules.users.service import AuthService

_bearer = HTTPBearer(auto_error=False)  # error kita yang atur, formatnya konsisten


def get_auth_service(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    return AuthService(UserRepository(db))


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise UnauthorizedError
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError, KeyError):
        raise UnauthorizedError from None
    user = UserRepository(db).get_by_id(user_id)
    # Role dibaca dari database, bukan dari token: perubahan role/penonaktifan langsung berlaku.
    if user is None or not user.is_active:
        raise UnauthorizedError
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: RoleName) -> Callable[[User], User]:
    allowed = {role.value for role in roles}

    def checker(user: CurrentUser) -> User:
        if user.role.name not in allowed:
            raise ForbiddenError
        return user

    return checker
