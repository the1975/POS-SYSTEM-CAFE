from sqlalchemy import select

from app.modules.payments.model import Payment

API = "/api/v1"


def _place(client, menu, key, method="CASH"):
    body = {
        "customer_name": "Leo",
        "items": [{"product_id": str(menu["es_teh"]), "quantity": 1}],
        "payment_method": method,
    }
    r = client.post(f"{API}/orders", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 201
    return r.json()["data"]


def _detail(client, order):
    return client.get(
        f"{API}/orders/{order['order_id']}",
        headers={"X-Tracking-Token": order["tracking_token"]},
    )


def test_customer_sees_waiting_cash_then_paid(client, menu, db, staff_headers):
    order = _place(client, menu, "kunci-detail-001")
    data = _detail(client, order).json()["data"]
    assert (data["status"], data["payment_status"]) == ("PENDING", "WAITING_CASH")
    assert "payment_id" not in data  # id internal pembayaran tidak dibocorkan ke customer

    headers = staff_headers("CASHIER", "kasir@example.com")
    confirm = client.post(
        f"{API}/payments/{db.scalar(select(Payment.id))}/cash-confirm",
        json={"cash_received": order["total"]},
        headers=headers,
    )
    assert confirm.status_code == 200

    data = _detail(client, order).json()["data"]
    assert (data["status"], data["payment_status"]) == ("CONFIRMED", "PAID")


def test_qris_order_detail_shows_pending_payment(client, menu):
    order = _place(client, menu, "kunci-detail-002", method="QRIS")
    data = _detail(client, order).json()["data"]
    assert data["payment_status"] == "PENDING"
