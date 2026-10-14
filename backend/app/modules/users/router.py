"""Endpoint login staff. (Logout menyusul: token JWT stateless, cukup dibuang di client.)"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.responses import DataResponse
from app.modules.users.dependencies import CurrentUser, get_auth_service
from app.modules.users.schema import LoginIn, LoginOut, UserOut
from app.modules.users.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=DataResponse[LoginOut])
def login(body: LoginIn, service: Annotated[AuthService, Depends(get_auth_service)]):
    return DataResponse(data=service.login(body))


@router.get("/me", response_model=DataResponse[UserOut])
def me(user: CurrentUser):
    return DataResponse(data=UserOut(id=user.id, name=user.name, role=user.role.name))
