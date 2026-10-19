"""Endpoint manajemen pengguna. Hanya ADMIN (di kode OWNER = ADMIN)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.responses import DataResponse, PageResponse
from app.db.dependencies import get_db
from app.modules.users.admin_service import UserAdminService
from app.modules.users.dependencies import require_roles
from app.modules.users.model import RoleName, User
from app.modules.users.repository import UserRepository
from app.modules.users.schema import RoleOut, UserCreateIn, UserItem, UserUpdateIn

router = APIRouter(prefix="/users", tags=["users"])

AdminUser = Annotated[User, Depends(require_roles(RoleName.ADMIN))]


def get_user_admin_service(db: Annotated[Session, Depends(get_db)]) -> UserAdminService:
    return UserAdminService(UserRepository(db))


ServiceDep = Annotated[UserAdminService, Depends(get_user_admin_service)]


@router.get("", response_model=PageResponse[UserItem])
def list_users(
    service: ServiceDep,
    admin: AdminUser,
    role_id: uuid.UUID | None = None,
    is_active: bool | None = None,
    search: Annotated[str | None, Query(max_length=100)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    items, pagination = service.list_users(
        role_id=role_id, is_active=is_active, search=search, page=page, page_size=page_size
    )
    return PageResponse(data=items, pagination=pagination)


@router.get("/roles", response_model=DataResponse[list[RoleOut]])
def list_roles(service: ServiceDep, admin: AdminUser):
    return DataResponse(data=service.list_roles())


@router.post("", status_code=201, response_model=DataResponse[UserItem])
def create_user(body: UserCreateIn, service: ServiceDep, admin: AdminUser):
    return DataResponse(data=service.create(body, admin))


@router.patch("/{user_id}", response_model=DataResponse[UserItem])
def update_user(user_id: uuid.UUID, body: UserUpdateIn, service: ServiceDep, admin: AdminUser):
    return DataResponse(data=service.update(user_id, body, admin))
