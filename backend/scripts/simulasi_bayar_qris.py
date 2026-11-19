"""Simulasi provider QRIS membayar sebuah pesanan (hanya untuk uji lokal, provider mock).

Pakai:  python -m scripts.simulasi_bayar_qris MC-0001
Syarat: PAYMENT_WEBHOOK_SECRET terisi di .env, backend sedang jalan, QR sudah tampil di halaman pesanan.
"""

import json
import sys
import urllib.error
import urllib.request
import uuid

from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import get_session_factory
from app.modules.orders.model import Order
from app.modules.payments.mock_provider import MockQrisProvider
from app.modules.payments.model import Payment

BASE = "http://localhost:8000/api/v1"


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Pakai: python -m scripts.simulasi_bayar_qris NOMOR_PESANAN")
    secret = get_settings().payment_webhook_secret
    if not secret:
        sys.exit("PAYMENT_WEBHOOK_SECRET belum diisi di .env (lalu restart backend).")

    with get_session_factory()() as db:
        payment = db.scalar(
            select(Payment)
            .join(Order, Order.id == Payment.order_id)
            .where(Order.order_number == sys.argv[1])
            .order_by(Payment.created_at.desc())
            .limit(1)
        )
    if payment is None:
        sys.exit("Pesanan tidak ditemukan.")
    if not payment.provider_transaction_id:
        sys.exit("Belum ada tagihan QRIS. Buka halaman pesanan dulu sampai QR tampil.")

    body = json.dumps(
        {
            "event_id": str(uuid.uuid4()),
            "event_type": "payment.paid",
            "transaction_id": payment.provider_transaction_id,
            "amount": str(payment.amount),
        }
    ).encode()
    signature = MockQrisProvider(webhook_secret=secret.get_secret_value()).sign(body)
    req = urllib.request.Request(
        f"{BASE}/payments/webhook",
        data=body,
        headers={"Content-Type": "application/json", "X-Signature": signature},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as res:
            print(res.status, res.read().decode())
    except urllib.error.HTTPError as err:
        print(err.code, err.read().decode())


main()
