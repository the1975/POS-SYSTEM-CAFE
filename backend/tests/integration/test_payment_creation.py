from sqlalchemy import func, select

from app.modules.orders.model import Order
from app.modules.payments.model import Payment

API = "/api/v1"


def _post(client, menu, items, key, method="CASH"):
    body = {
        "customer_name": "Leo",
        "items": [{"product_id": str(menu[n]), "quantity": q} for n, q in items],
        "payment_method": method,
    }
    return client.post(f"{API}/orders", json=body, headers={"Idempotency-Key": key})


def _count_payments(db) -> int:
    return db.scalar(select(func.count()).select_from(Payment))


def test_cash_order_creates_payment_waiting_for_cashier(client, menu, db):
    assert _post(client, menu, [("es_teh", 2)], "kunci-bayar-001", "CASH").status_code == 201
    order = db.scalars(select(Order)).one()
    payment = db.scalars(select(Payment)).one()
    assert payment.order_id == order.id
    assert (payment.payment_method, payment.status) == ("CASH", "WAITING_CASH")
    assert payment.amount == order.total
    assert payment.paid_at is None and payment.cash_received is None


def test_qris_order_creates_pending_payment(client, menu, db):
    assert _post(client, menu, [("es_teh", 1)], "kunci-bayar-002", "QRIS").status_code == 201
    payment = db.scalars(select(Payment)).one()
    assert (payment.payment_method, payment.status) == ("QRIS", "PENDING")
    assert payment.provider_transaction_id is None
    assert payment.expires_at is not None


def test_replaying_same_request_does_not_create_second_payment(client, menu, db):
    _post(client, menu, [("es_teh", 1)], "kunci-bayar-003")
    again = _post(client, menu, [("es_teh", 1)], "kunci-bayar-003")
    assert again.status_code == 200
    assert _count_payments(db) == 1


def test_rejected_order_creates_no_payment(client, menu, db):
    assert _post(client, menu, [("nasi", 6)], "kunci-bayar-004").status_code == 409
    assert _count_payments(db) == 0
