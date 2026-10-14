"""Aturan bisnis login staff."""

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.users.exceptions import InvalidCredentialsError
from app.modules.users.repository import UserRepository
from app.modules.users.schema import LoginIn, LoginOut, UserOut

# Hash palsu: dipakai saat email tidak ditemukan, supaya waktu respons tetap sama dan
# tidak membocorkan apakah email itu terdaftar.
_DUMMY_HASH = hash_password("password-palsu-untuk-menyamakan-waktu")


class AuthService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    def login(self, data: LoginIn) -> LoginOut:
        user = self.repo.get_by_email(data.email)
        valid = verify_password(data.password, user.password_hash if user else _DUMMY_HASH)
        if user is None or not valid or not user.is_active:
            raise InvalidCredentialsError
        return LoginOut(
            access_token=create_access_token(user.id, user.role.name),
            user=UserOut(id=user.id, name=user.name, role=user.role.name),
        )
