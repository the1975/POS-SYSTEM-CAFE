import uuid

from pydantic import BaseModel, Field


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
