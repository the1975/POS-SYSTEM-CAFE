from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import jwt
import pytest
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.modules.users.dependencies import require_roles
from app.modules.users.exceptions import ForbiddenError
from app.modules.users.model import Role, RoleName, User

API = "/api/v1"
PASSWORD = "password-uji-12345"


def _make_user(db, role_name="CASHIER", email="kasir@example.com", active=True) -> User:
    role = db.scalar(select(Role).where(Role.name == role_name))
    if role is None:
        role = Role(name=role_name)
        db.add(role)
        db.flush()
    user = User(
        role_id=role.id,
        name=f"Staf {role_name}",
        email=email,
        password_hash=hash_password(PASSWORD),
        is_active=active,
    )
    db.add(user)
    db.commit()
    return user


def _login(client, email="kasir@example.com", password=PASSWORD):
    return client.post(f"{API}/auth/login", json={"email": email, "password": password})


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_login_returns_token_and_user_without_password(client, db):
    _make_user(db)
    r = _login(client)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["token_type"] == "bearer" and data["access_token"]
    assert data["user"]["role"] == "CASHIER"
    assert "password" not in r.text and "hash" not in r.text


def test_login_email_is_case_insensitive(client, db):
    _make_user(db)
    assert _login(client, email="KASIR@Example.com").status_code == 200


@pytest.mark.parametrize("case", ["wrong_password", "unknown_email", "inactive_account"])
def test_login_failures_all_look_the_same(client, db, case):
    _make_user(db, active=(case != "inactive_account"))
    email = "tidak-ada@example.com" if case == "unknown_email" else "kasir@example.com"
    password = "password-salah-banget" if case == "wrong_password" else PASSWORD
    r = _login(client, email=email, password=password)
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "INVALID_CREDENTIALS"
    assert r.json()["error"]["message"] == "Email atau password salah."


def test_me_returns_current_user(client, db):
    _make_user(db)
    token = _login(client).json()["data"]["access_token"]
    r = client.get(f"{API}/auth/me", headers=_auth(token))
    assert r.status_code == 200
    assert r.json()["data"]["role"] == "CASHIER"


def test_me_requires_token(client):
    r = client.get(f"{API}/auth/me")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "UNAUTHORIZED"


def test_me_rejects_garbage_token(client):
    assert client.get(f"{API}/auth/me", headers=_auth("token-ngawur")).status_code == 401


def test_me_rejects_expired_token(client, db):
    user = _make_user(db)
    secret = get_settings().jwt_secret.get_secret_value()
    expired = jwt.encode(
        {"sub": str(user.id), "exp": datetime.now(UTC) - timedelta(minutes=1)},
        secret,
        algorithm="HS256",
    )
    assert client.get(f"{API}/auth/me", headers=_auth(expired)).status_code == 401


def test_require_roles_allows_listed_role():
    cashier = SimpleNamespace(role=SimpleNamespace(name="CASHIER"))
    checker = require_roles(RoleName.CASHIER, RoleName.ADMIN)
    assert checker(cashier) is cashier


def test_require_roles_blocks_other_role():
    kitchen = SimpleNamespace(role=SimpleNamespace(name="KITCHEN"))
    with pytest.raises(ForbiddenError):
        require_roles(RoleName.CASHIER, RoleName.ADMIN)(kitchen)
