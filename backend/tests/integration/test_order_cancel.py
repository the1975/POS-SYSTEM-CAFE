import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update

from app.modules.inventory.model import Inventory, StockMovement, StockReservation
from app.modules.orders.expiration import build_expiration_service
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import Order
from app.modules.payments.model import Payment

API = "/api/v1"


def _place(client, menu, key, items=(("es_teh", 1),), method="CASH"):
    body = {
        "customer_name": "Leo",
        "items": [{"product_id": str(menu[n]), "quantity": q} for n, q in items],
        "payment_method": method,
    }
    r = client.post(f"{API}/orders", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 201
    return r.json()["data"]


def _cancel(client, order, token="pakai-token-order"):
    headers = {}
    if token is not None:
        headers["X-Tracking-Token"] = (
            order["tracking_token"] if token == "pakai-token-order" else token
        )
    return client.post(f"{API}/orders/{order['order_id']}/cancel", headers=headers)


def _stock(db, menu, name="es_teh"):
    row = db.execute(
        select(Inventory.quantity_available, Inventory.quantity_reserved).where(
            Inventory.product_id == menu[name]
        )
    ).one()
    return tuple(row)


def test_customer_cancels_unpaid_order_and_stock_returns(client, menu, db):
    order = _place(client, menu, "kunci-batal-001", items=(("es_teh", 2),))
    assert _stock(db, menu) == (8, 2)

    r = _cancel(client, order)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["order_number"] == order["order_number"]
    assert data["status"] == "CANCELLED" and data["refund_status"] is None

    assert _stock(db, menu) == (10, 0)
    status, released_at = db.execute(
        select(StockReservation.status, StockReservation.released_at)
    ).one()
    assert status == "CANCELLED" and released_at is not None
    movements = [
        tuple(m) for m in db.execute(select(StockMovement.movement_type, StockMovement.quantity))
    ]
    assert sorted(movements) == [("RELEASE", 2), ("RESERVATION", -2)]
    order_status, cancelled_at = db.execute(select(Order.status, Order.cancelled_at)).one()
    assert order_status == "CANCELLED" and cancelled_at is not None
    assert db.scalar(select(Payment.status)) == "FAILED"
    reasons = db.execute(
        select(OrderStatusHistory.reason).where(OrderStatusHistory.to_status == "CANCELLED")
    ).all()
    assert [r[0] for r in reasons] == ["Dibatalkan oleh customer"]


def test_cancelling_twice_does_not_release_stock_twice(client, menu, db):
    order = _place(client, menu, "kunci-batal-002", items=(("es_teh", 2),))
    assert _cancel(client, order).status_code == 200
    again = _cancel(client, order)
    assert again.status_code == 200 and again.json()["data"]["status"] == "CANCELLED"
    assert _stock(db, menu) == (10, 0)
    releases = [m for m in db.scalars(select(StockMovement.movement_type)) if m == "RELEASE"]
    assert len(releases) == 1


def test_missing_or_wrong_token_looks_like_unknown_order(client, menu, db):
    order = _place(client, menu, "kunci-batal-003")
    for token in (None, "token-ngawur"):
        r = _cancel(client, order, token=token)
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "ORDER_NOT_FOUND"
    assert db.scalar(select(Order.status)) == "PENDING"
    assert _stock(db, menu) == (9, 1)


def test_unknown_order_returns_404(client):
    r = client.post(f"{API}/orders/{uuid.uuid4()}/cancel", headers={"X-Tracking-Token": "apa-saja"})
    assert r.status_code == 404


def test_paid_order_cannot_be_cancelled_by_customer(client, menu, db, staff_headers):
    order = _place(client, menu, "kunci-batal-004", items=(("es_teh", 2),))
    pid, amount = db.execute(select(Payment.id, Payment.amount)).one()
    confirm = client.post(
        f"{API}/payments/{pid}/cash-confirm",
        json={"cash_received": str(amount)},
        headers=staff_headers("CASHIER", "kasir@example.com"),
    )
    assert confirm.status_code == 200

    r = _cancel(client, order)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "ORDER_NOT_CANCELLABLE"
    assert db.scalar(select(Order.status)) == "CONFIRMED"
    assert _stock(db, menu) == (8, 0)  # stok tetap terjual


def test_cancelled_cash_order_cannot_be_paid_anymore(client, menu, db, staff_headers):
    order = _place(client, menu, "kunci-batal-005")
    pid, amount = db.execute(select(Payment.id, Payment.amount)).one()
    assert _cancel(client, order).status_code == 200

    r = client.post(
        f"{API}/payments/{pid}/cash-confirm",
        json={"cash_received": str(amount)},
        headers=staff_headers("CASHIER", "kasir@example.com"),
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PAYMENT_INVALID_STATE"
    assert _stock(db, menu) == (10, 0)


def test_cancelled_qris_order_cannot_get_a_qr(client, menu):
    order = _place(client, menu, "kunci-batal-006", method="QRIS")
    assert _cancel(client, order).status_code == 200
    r = client.post(
        f"{API}/payments/qris",
        json={"order_id": order["order_id"]},
        headers={"X-Tracking-Token": order["tracking_token"]},
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PAYMENT_INVALID_STATE"


def test_cancelling_an_already_expired_order_is_a_harmless_repeat(client, menu, db):
    order = _place(client, menu, "kunci-batal-007", items=(("es_teh", 2),))
    db.execute(update(StockReservation).values(expires_at=datetime.now(UTC) - timedelta(minutes=1)))
    db.commit()
    assert build_expiration_service(db).expire_due(datetime.now(UTC)) == 1

    r = _cancel(client, order)
    assert r.status_code == 200 and r.json()["data"]["status"] == "CANCELLED"
    assert _stock(db, menu) == (10, 0)  # tidak dikembalikan dua kali
    releases = [m for m in db.scalars(select(StockMovement.movement_type)) if m == "RELEASE"]
    assert len(releases) == 1


def test_multi_item_cancel_releases_every_line(client, menu, db):
    order = _place(client, menu, "kunci-batal-008", items=(("es_teh", 2), ("nasi", 1)))
    assert (_stock(db, menu), _stock(db, menu, "nasi")) == ((8, 2), (4, 1))
    assert _cancel(client, order).status_code == 200
    assert (_stock(db, menu), _stock(db, menu, "nasi")) == ((10, 0), (5, 0))
