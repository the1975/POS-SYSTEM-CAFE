"""Kontrak payment provider. Provider asli (Midtrans, Xendit, dll.) cukup menulis satu kelas
yang memenuhi kontrak ini; service dan endpoint tidak perlu diubah."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class ProviderTransaction:
    transaction_id: str
    payment_url: str


@dataclass(frozen=True)
class ProviderEvent:
    """Webhook yang sudah diurai ke bentuk netral (apa pun format aslinya)."""

    event_id: str
    event_type: str  # "payment.paid" | "payment.failed" | lainnya (diabaikan)
    transaction_id: str
    amount: Decimal
    payload: dict


EVENT_PAID = "payment.paid"
EVENT_FAILED = "payment.failed"


class PaymentProvider(Protocol):
    name: str

    def create_qris_transaction(
        self, *, reference: str, amount: Decimal, expires_at: datetime | None
    ) -> ProviderTransaction:
        """`reference` = kunci idempotensi: referensi sama harus menghasilkan transaksi sama."""
        ...

    def payment_url(self, transaction_id: str) -> str: ...

    def verify_webhook(self, *, raw_body: bytes, signature: str | None) -> bool:
        """Cek tanda tangan pada body MENTAH (sebelum di-parse)."""
        ...

    def parse_webhook(self, raw_body: bytes) -> ProviderEvent:
        """Melempar InvalidWebhookPayloadError bila isi tidak sesuai format."""
        ...
