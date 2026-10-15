import json

import pytest
from sqlalchemy import func, select

from app.core.config import get_settings
from app.modules.inventory.model import Inventory, StockMovement, StockReservation
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import Order
from app.modules.payments.mock_provider import MockQrisProvider
from app.modules.payments.model import Payment, PaymentEvent

API = "/api/v1"


def _provider() -> MockQrisProvider:
    return MockQrisProvider(webhook_secret=get_settings().payment_webhook_secret.get_secret_value())


def _qris_order(client, menu, key):
    """Order QRIS + minta QR, supaya payment punya provider_transaction_id."""
    body = {
        "customer_name": "Leo",
        "items": [{"product_id": str(menu["es_teh"]), "quantity": 1}],
        "payment_method": "QRIS",
    }
    order = client.post(f"{API}/orders", json=body, headers={"Idempotency-Key": key}).json()["data"]
    qr = client.post(
        f"{API}/payments/qris",
        json={"order_id": order["order_id"]},
        headers={"X-Tracking-Token": order["tracking_token"]},
    )
    assert qr.status_code == 200
    return order


def _payment(db):
    return db.execute(select(Payment.id, Payment.amount, Payment.provider_transaction_id)).one()


def _send(client, payload: dict, signature=None):
    raw = json.dumps(payload).encode()
    return _send_raw(client, raw, _provider().sign(raw) if signature is None else signature)


def _send_raw(client, raw: bytes, signature):
    headers = {"Content-Type": "application/json"}
    if signature is not None:
        headers["X-Signature"] = signature
    return client.post(f"{API}/payments/webhook", content=raw, headers=headers)


def _event(pay, event_id="evt-001", event_type="payment.paid", amount=None):
    _, price, tx_id = pay
    return {
        "event_id": event_id,
        "event_type": event_type,
        "transaction_id": tx_id,
        "amount": str(price if amount is None else amount),
    }


def _stock(db, menu):
    row = db.execute(
        select(Inventory.quantity_available, Inventory.quantity_reserved).where(
            Inventory.product_id == menu["es_teh"]
        )
    ).one()
    return tuple(row)


def _count(db, model) -> int:
    return db.scalar(select(func.count()).select_from(model)) or 0


def test_paid_webhook_confirms_order_and_converts_stock(client, menu, db):
    order = _qris_order(client, menu, "kunci-hook-001")
    pay = _payment(db)

    r = _send(client, _event(pay))
    assert r.status_code == 200
    assert r.json()["data"]["result"] == "processed"

    status, paid_at = db.execute(select(Payment.status, Payment.paid_at)).one()
    assert status == "PAID" and paid_at is not None
    assert db.scalar(select(Order.status)) == "CONFIRMED"
    assert db.scalar(select(StockReservation.status)) == "CONVERTED"
    assert _stock(db, menu) == (9, 0)
    movements = [
        tuple(m) for m in db.execute(select(StockMovement.movement_type, StockMovement.quantity))
    ]
    assert sorted(movements) == [("RESERVATION", -1), ("SALE", -1)]
    confirmed_by = db.scalar(
        select(OrderStatusHistory.changed_by).where(OrderStatusHistory.to_status == "CONFIRMED")
    )
    assert confirmed_by is None  # dilakukan sistem (webhook), bukan staff
    assert db.scalar(select(PaymentEvent.processed_at)) is not None

    detail = client.get(
        f"{API}/orders/{order['order_id']}", headers={"X-Tracking-Token": order["tracking_token"]}
    ).json()["data"]
    assert (detail["status"], detail["payment_status"]) == ("CONFIRMED", "PAID")


def test_same_event_twice_is_processed_once(client, menu, db):
    _qris_order(client, menu, "kunci-hook-002")
    event = _event(_payment(db))
    assert _send(client, event).json()["data"]["result"] == "processed"
    again = _send(client, event)
    assert again.status_code == 200
    assert again.json()["data"]["result"] == "duplicate"
    assert _stock(db, menu) == (9, 0)
    assert _count(db, PaymentEvent) == 1
    sales = [m for m in db.scalars(select(StockMovement.movement_type)) if m == "SALE"]
    assert len(sales) == 1


def test_different_event_for_already_paid_payment_is_ignored(client, menu, db):
    _qris_order(client, menu, "kunci-hook-003")
    pay = _payment(db)
    assert _send(client, _event(pay, "evt-a")).json()["data"]["result"] == "processed"
    r = _send(client, _event(pay, "evt-b"))
    assert r.status_code == 200 and r.json()["data"]["result"] == "ignored"
    assert _stock(db, menu) == (9, 0)
    assert _count(db, PaymentEvent) == 2


@pytest.mark.parametrize("signature", ["tanda-tangan-salah", None])
def test_bad_or_missing_signature_is_rejected(client, menu, db, signature):
    _qris_order(client, menu, "kunci-hook-004")
    raw = json.dumps(_event(_payment(db))).encode()
    r = _send_raw(client, raw, signature)
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "INVALID_SIGNATURE"
    assert db.scalar(select(Payment.status)) == "PENDING"
    assert _count(db, PaymentEvent) == 0


def test_unknown_transaction_returns_404(client):
    r = _send(
        client,
        {
            "event_id": "evt-x",
            "event_type": "payment.paid",
            "transaction_id": "MOCK-tidak-ada",
            "amount": "1000",
        },
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "PAYMENT_NOT_FOUND"


def test_amount_mismatch_is_rejected_and_nothing_changes(client, menu, db):
    _qris_order(client, menu, "kunci-hook-005")
    pay = _payment(db)
    r = _send(client, _event(pay, amount=pay.amount + 1))
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PAYMENT_AMOUNT_MISMATCH"
    assert db.scalar(select(Payment.status)) == "PENDING"
    assert db.scalar(select(Order.status)) == "PENDING"
    assert _stock(db, menu) == (9, 1)
    assert _count(db, PaymentEvent) == 0  # dibatalkan bersama, provider boleh kirim ulang


def test_failed_event_marks_payment_failed_but_order_stays(client, menu, db):
    _qris_order(client, menu, "kunci-hook-006")
    r = _send(client, _event(_payment(db), event_type="payment.failed"))
    assert r.json()["data"]["result"] == "processed"
    assert db.scalar(select(Payment.status)) == "FAILED"
    assert db.scalar(select(Order.status)) == "PENDING"
    assert _stock(db, menu) == (9, 1)  # pelepasan stok menyusul di tahap kedaluwarsa


def test_paid_event_for_failed_payment_is_not_applied(client, menu, db):
    _qris_order(client, menu, "kunci-hook-007")
    pay = _payment(db)
    _send(client, _event(pay, "evt-f", "payment.failed"))
    r = _send(client, _event(pay, "evt-p", "payment.paid"))
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PAYMENT_INVALID_STATE"
    assert db.scalar(select(Payment.status)) == "FAILED"
    assert db.scalar(select(Order.status)) == "PENDING"


@pytest.mark.parametrize("raw", [b'{"event_id": "x"}', b"bukan json sama sekali"])
def test_signed_but_malformed_payload_is_rejected(client, raw):
    r = _send_raw(client, raw, _provider().sign(raw))
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "INVALID_WEBHOOK_PAYLOAD"
