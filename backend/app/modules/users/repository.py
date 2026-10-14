"""Akses database user. Hanya query; aturan login ada di AuthService."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.users.model import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(func.lower(User.email) == email.strip().lower())
        return self.db.scalar(stmt)

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)
