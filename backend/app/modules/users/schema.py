import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, model_validator


class LoginIn(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=200)


class UserOut(BaseModel):
    """Password/hash tidak pernah ikut keluar."""

    id: uuid.UUID
    name: str
    role: str


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


_Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
_Email = Annotated[
    str,
    StringConstraints(strip_whitespace=True, max_length=255, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
]


class RoleOut(BaseModel):
    id: uuid.UUID
    name: str


class UserItem(BaseModel):
    """Data akun untuk admin. Password/hash tidak pernah ikut keluar."""

    id: uuid.UUID
    name: str
    email: str
    role: str
    role_id: uuid.UUID
    is_active: bool
    created_at: datetime


class UserCreateIn(BaseModel):
    name: _Name
    email: _Email
    password: str = Field(min_length=12, max_length=200)
    role_id: uuid.UUID


class UserUpdateIn(BaseModel):
    name: _Name | None = None
    role_id: uuid.UUID | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def _at_least_one(self):
        if self.name is None and self.role_id is None and self.is_active is None:
            raise ValueError("Isi minimal satu: name, role_id, atau is_active")
        return self
