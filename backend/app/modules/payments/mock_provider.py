"""Provider tiruan untuk development dan test. URL-nya TIDAK bisa dibayar sungguhan."""

from datetime import datetime
from decimal import Decimal

from app.modules.payments.provider import ProviderTransaction


class MockQrisProvider:
    name = "MOCK_QRIS"

    def create_qris_transaction(
        self, *, reference: str, amount: Decimal, expires_at: datetime | None
    ) -> ProviderTransaction:
        # ID dibentuk dari reference: panggilan ulang dengan reference sama = transaksi sama
        # (meniru idempotency key provider asli).
        transaction_id = f"MOCK-{reference}"
        return ProviderTransaction(transaction_id, self.payment_url(transaction_id))

    def payment_url(self, transaction_id: str) -> str:
        return f"https://mock-pay.invalid/qris/{transaction_id}"
