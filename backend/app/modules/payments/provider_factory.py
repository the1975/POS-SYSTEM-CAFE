"""Satu tempat memilih provider. Saat provider asli sudah diputuskan, ganti di sini saja."""

from app.core.config import get_settings
from app.modules.payments.mock_provider import MockQrisProvider
from app.modules.payments.provider import PaymentProvider


def get_payment_provider() -> PaymentProvider:
    secret = get_settings().payment_webhook_secret
    return MockQrisProvider(webhook_secret=secret.get_secret_value() if secret else None)
