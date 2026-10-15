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


class PaymentProvider(Protocol):
    name: str

    def create_qris_transaction(
        self, *, reference: str, amount: Decimal, expires_at: datetime | None
    ) -> ProviderTransaction:
        """`reference` = kunci idempotensi: referensi sama harus menghasilkan transaksi sama."""
        ...

    def payment_url(self, transaction_id: str) -> str: ...
