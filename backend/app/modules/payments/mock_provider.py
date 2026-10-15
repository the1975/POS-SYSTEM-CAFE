"""Provider tiruan untuk development dan test. URL-nya TIDAK bisa dibayar sungguhan."""

import hashlib
import hmac
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

from app.modules.payments.exceptions import InvalidWebhookPayloadError
from app.modules.payments.provider import ProviderEvent, ProviderTransaction


class MockQrisProvider:
    name = "MOCK_QRIS"

    def __init__(self, webhook_secret: str | None = None) -> None:
        self._secret = webhook_secret

    def create_qris_transaction(
        self, *, reference: str, amount: Decimal, expires_at: datetime | None
    ) -> ProviderTransaction:
        # ID dibentuk dari reference: panggilan ulang dengan reference sama = transaksi sama
        # (meniru idempotency key provider asli).
        transaction_id = f"MOCK-{reference}"
        return ProviderTransaction(transaction_id, self.payment_url(transaction_id))

    def payment_url(self, transaction_id: str) -> str:
        return f"https://mock-pay.invalid/qris/{transaction_id}"

    def sign(self, raw_body: bytes) -> str:
        """Dipakai test/simulator untuk meniru provider. Provider asli menandatangani di sisinya."""
        return hmac.new((self._secret or "").encode(), raw_body, hashlib.sha256).hexdigest()

    def verify_webhook(self, *, raw_body: bytes, signature: str | None) -> bool:
        # Rahasia belum diisi = semua webhook ditolak (aman secara default).
        if not self._secret or not signature:
            return False
        return hmac.compare_digest(self.sign(raw_body), signature)

    def parse_webhook(self, raw_body: bytes) -> ProviderEvent:
        try:
            data = json.loads(raw_body)
            return ProviderEvent(
                event_id=str(data["event_id"]),
                event_type=str(data["event_type"]),
                transaction_id=str(data["transaction_id"]),
                amount=Decimal(str(data["amount"])),
                payload=data,
            )
        except (ValueError, KeyError, TypeError, InvalidOperation):
            raise InvalidWebhookPayloadError from None
