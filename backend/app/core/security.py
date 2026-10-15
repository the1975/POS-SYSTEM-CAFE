"""Keamanan: hashing password staff/admin + token tracking order customer.
RBAC dan token pickup menyusul di fase berikutnya."""

import base64
import hashlib
import hmac
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.core.config import get_settings

# Argon2id dengan parameter default library (aman untuk penggunaan umum).
_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


# ---- Token tracking order (customer guest) ----------------------------------------------
# Token = HMAC-SHA256(rahasia server, order_id): 256-bit, tidak bisa ditebak tanpa rahasia.
# Kenapa diturunkan, bukan acak murni? Supaya request ulang dengan Idempotency-Key yang sama
# (mis. respons pertama hilang karena sinyal HP putus) bisa mengembalikan token yang SAMA,
# tanpa menyimpan token mentah di database. Yang disimpan tetap HASH-nya saja.


def derive_tracking_token(order_id: uuid.UUID) -> str:
    secret = get_settings().tracking_token_secret
    if secret is None:
        raise RuntimeError("TRACKING_TOKEN_SECRET belum diisi di .env")
    digest = hmac.new(secret.get_secret_value().encode(), order_id.bytes, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def hash_token(token: str) -> str:
    # SHA-256 cukup untuk token berentropi tinggi (tidak perlu salt/argon2 seperti password).
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token(token: str, token_hash: str) -> bool:
    # compare_digest: waktu perbandingan konstan, tidak membocorkan kecocokan sebagian.
    return hmac.compare_digest(hash_token(token), token_hash)


# ---- Token login staff (JWT) --------------------------------------------------------------
# Stateless: server tidak menyimpan sesi. Masa berlaku pendek (access_token_minutes).


def _jwt_secret() -> str:
    secret = get_settings().jwt_secret
    if secret is None:
        raise RuntimeError("JWT_SECRET belum diisi di .env")
    return secret.get_secret_value()


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=get_settings().access_token_minutes),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm="HS256")


def decode_access_token(token: str) -> dict:
    """Melempar jwt.PyJWTError bila token palsu, rusak, atau kedaluwarsa."""
    return jwt.decode(
        token, _jwt_secret(), algorithms=["HS256"], options={"require": ["exp", "sub"]}
    )


# ---- Token pickup (diambil customer saat order READY) -----------------------------------
# Pola sama dengan token tracking, tapi "label" HMAC-nya berbeda: token tracking tidak bisa
# dipakai sebagai token pickup (dan sebaliknya). Yang disimpan di database tetap HASH-nya.


def derive_pickup_token(order_id: uuid.UUID) -> str:
    secret = get_settings().tracking_token_secret
    if secret is None:
        raise RuntimeError("TRACKING_TOKEN_SECRET belum diisi di .env")
    digest = hmac.new(
        secret.get_secret_value().encode(), b"pickup:" + order_id.bytes, hashlib.sha256
    ).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
