from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select, update

from app.modules.payments.model import Payment

API = "/api/v1"


def _place(client, menu, key, method="QRIS"):
    body = {
        "customer_name": "Leo",
        "items": [{"product_id": str(menu["es_teh"]), "quantity": 1}],
        "payment_method": method,
    }
    r = client.post(f"{API}/orders", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 201
    return r.json()["data"]


def _qris(client, order, token="pakai-token-order"):
    headers = (
        {}
        if token is None
        else {
            "X-Tracking-Token": order["tracking_token"] if token == "pakai-token-order" else token
        }
    )
    return client.post(
        f"{API}/payments/qris", json={"order_id": order["order_id"]}, headers=headers
    )


def _payment(db):
    return db.execute(select(Payment.id, Payment.provider_transaction_id, Payment.status)).one()


def test_qris_creates_provider_transaction_and_returns_payment_url(client, menu, db):
    order = _place(client, menu, "kunci-qris-001")
    r = _qris(client, order)
    assert r.status_code == 200
    data = r.json()["data"]
    pid, tx_id, status = _payment(db)
    assert data["payment_id"] == str(pid)
    assert data["payment_status"] == "PENDING" and status == "PENDING"  # belum dibayar
    assert data["payment_url"] == f"https://mock-pay.invalid/qris/MOCK-{pid}"
    assert data["expires_at"] is not None
    assert tx_id == f"MOCK-{pid}"


def test_asking_twice_returns_the_same_qr(client, menu, db):
    order = _place(client, menu, "kunci-qris-002")
    first = _qris(client, order).json()["data"]
    second = _qris(client, order)
    assert second.status_code == 200
    assert second.json()["data"]["payment_url"] == first["payment_url"]
    assert _payment(db).provider_transaction_id == f"MOCK-{first['payment_id']}"


def test_missing_or_wrong_token_looks_like_unknown_order(client, menu, db):
    order = _place(client, menu, "kunci-qris-003")
    for token in (None, "token-ngawur"):
        r = _qris(client, order, token=token)
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "ORDER_NOT_FOUND"
    assert _payment(db).provider_transaction_id is None


def test_unknown_order_returns_404(client):
    r = client.post(
        f"{API}/payments/qris",
        json={"order_id": str(uuid4())},
        headers={"X-Tracking-Token": "apa-saja"},
    )
    assert r.status_code == 404


def test_cash_order_cannot_get_qris(client, menu):
    order = _place(client, menu, "kunci-qris-004", method="CASH")
    r = _qris(client, order)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PAYMENT_NOT_QRIS"


def test_paid_payment_cannot_get_a_new_qr(client, menu, db):
    order = _place(client, menu, "kunci-qris-005")
    db.execute(update(Payment).values(status="PAID"))
    db.commit()
    r = _qris(client, order)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PAYMENT_ALREADY_PAID"


def test_expired_payment_cannot_get_a_qr(client, menu, db):
    order = _place(client, menu, "kunci-qris-006")
    db.execute(update(Payment).values(expires_at=datetime.now(UTC) - timedelta(minutes=1)))
    db.commit()
    r = _qris(client, order)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PAYMENT_EXPIRED"
    assert _payment(db).provider_transaction_id is None


def test_missing_order_id_is_rejected(client):
    r = client.post(f"{API}/payments/qris", json={})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"
