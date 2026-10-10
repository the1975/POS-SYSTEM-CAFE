"""Keamanan: hashing password staff/admin + token tracking order customer.
RBAC dan token pickup menyusul di fase berikutnya."""
import base64
import hashlib
import hmac
import uuid

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
