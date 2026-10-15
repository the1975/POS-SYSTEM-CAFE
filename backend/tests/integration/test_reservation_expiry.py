import json
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update

from app.core.config import get_settings
from app.modules.inventory.model import Inventory, StockMovement, StockReservation
from app.modules.orders.expiration import build_expiration_service
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import Order
from app.modules.payments.mock_provider import MockQrisProvider
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


def _make_due(db, order=None):
    """Majukan waktu: batas reservasi jadi sudah lewat (untuk semua order, atau satu saja)."""
    stmt = update(StockReservation).values(expires_at=datetime.now(UTC) - timedelta(minutes=1))
    if order is not None:
        stmt = stmt.where(StockReservation.order_id == uuid.UUID(order["order_id"]))
    db.execute(stmt)
    db.commit()


def _run(db, batch_size=50) -> int:
    return build_expiration_service(db).expire_due(datetime.now(UTC), batch_size=batch_size)


def _stock(db, menu, name="es_teh"):
    row = db.execute(
        select(Inventory.quantity_available, Inventory.quantity_reserved).where(
            Inventory.product_id == menu[name]
        )
    ).one()
    return tuple(row)


def _detail(client, order):
    return client.get(
        f"{API}/orders/{order['order_id']}", headers={"X-Tracking-Token": order["tracking_token"]}
    ).json()["data"]


def test_expired_unpaid_order_releases_stock_and_is_cancelled(client, menu, db):
    order = _place(client, menu, "kunci-exp-001", items=(("es_teh", 2),))
    assert _stock(db, menu) == (8, 2)
    _make_due(db)

    assert _run(db) == 1

    status, released_at = db.execute(
        select(StockReservation.status, StockReservation.released_at)
    ).one()
    assert status == "EXPIRED" and released_at is not None
    assert _stock(db, menu) == (10, 0)  # stok kembali tersedia
    movements = [
        tuple(m) for m in db.execute(select(StockMovement.movement_type, StockMovement.quantity))
    ]
    assert sorted(movements) == [("RELEASE", 2), ("RESERVATION", -2)]
    order_status, cancelled_at = db.execute(select(Order.status, Order.cancelled_at)).one()
    assert order_status == "CANCELLED" and cancelled_at is not None
    assert db.scalar(select(Payment.status)) == "FAILED"
    cancelled_by = db.execute(
        select(OrderStatusHistory.changed_by).where(OrderStatusHistory.to_status == "CANCELLED")
    ).all()
    assert len(cancelled_by) == 1 and cancelled_by[0][0] is None  # dilakukan sistem

    detail = _detail(client, order)
    assert (detail["status"], detail["payment_status"]) == ("CANCELLED", "FAILED")


def test_only_due_orders_are_expired(client, menu, db):
    old = _place(client, menu, "kunci-exp-002")
    fresh = _place(client, menu, "kunci-exp-003")
    _make_due(db, old)

    assert _run(db) == 1
    assert _detail(client, old)["status"] == "CANCELLED"
    assert _detail(client, fresh)["status"] == "PENDING"
    assert _stock(db, menu) == (9, 1)  # yang baru masih menahan 1


def test_running_twice_changes_nothing_the_second_time(client, menu, db):
    _place(client, menu, "kunci-exp-004", items=(("es_teh", 2),))
    _make_due(db)
    assert _run(db) == 1
    assert _run(db) == 0
    assert _stock(db, menu) == (10, 0)  # tidak bertambah dua kali
    releases = [m for m in db.scalars(select(StockMovement.movement_type)) if m == "RELEASE"]
    assert len(releases) == 1


def test_multi_item_order_releases_every_line(client, menu, db):
    _place(client, menu, "kunci-exp-005", items=(("es_teh", 2), ("nasi", 1)))
    assert (_stock(db, menu), _stock(db, menu, "nasi")) == ((8, 2), (4, 1))
    _make_due(db)
    assert _run(db) == 1
    assert (_stock(db, menu), _stock(db, menu, "nasi")) == ((10, 0), (5, 0))


def test_paid_order_is_never_expired(client, menu, db, staff_headers):
    order = _place(client, menu, "kunci-exp-006", items=(("es_teh", 2),))
    pid, amount = db.execute(select(Payment.id, Payment.amount)).one()
    confirm = client.post(
        f"{API}/payments/{pid}/cash-confirm",
        json={"cash_received": str(amount)},
        headers=staff_headers("CASHIER", "kasir@example.com"),
    )
    assert confirm.status_code == 200
    _make_due(db)

    assert _run(db) == 0
    assert _detail(client, order)["status"] == "CONFIRMED"
    assert _stock(db, menu) == (8, 0)  # stok tetap terjual


def test_batch_size_limits_work_per_run(client, menu, db):
    for i in range(3):
        _place(client, menu, f"kunci-exp-10{i}")
    _make_due(db)
    assert _run(db, batch_size=2) == 2
    assert _run(db, batch_size=2) == 1
    assert _stock(db, menu) == (10, 0)


def test_cash_confirm_after_expiry_is_rejected(client, menu, db, staff_headers):
    _place(client, menu, "kunci-exp-007")
    pid, amount = db.execute(select(Payment.id, Payment.amount)).one()
    _make_due(db)
    assert _run(db) == 1

    r = client.post(
        f"{API}/payments/{pid}/cash-confirm",
        json={"cash_received": str(amount)},
        headers=staff_headers("CASHIER", "kasir@example.com"),
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PAYMENT_INVALID_STATE"
    assert _stock(db, menu) == (10, 0)


def test_late_qris_webhook_after_expiry_is_rejected(client, menu, db):
    order = _place(client, menu, "kunci-exp-008", method="QRIS")
    qr = client.post(
        f"{API}/payments/qris",
        json={"order_id": order["order_id"]},
        headers={"X-Tracking-Token": order["tracking_token"]},
    )
    assert qr.status_code == 200
    pid, amount = db.execute(select(Payment.id, Payment.amount)).one()
    _make_due(db)
    assert _run(db) == 1

    raw = json.dumps(
        {
            "event_id": "evt-telat",
            "event_type": "payment.paid",
            "transaction_id": f"MOCK-{pid}",
            "amount": str(amount),
        }
    ).encode()
    signer = MockQrisProvider(
        webhook_secret=get_settings().payment_webhook_secret.get_secret_value()
    )
    r = client.post(
        f"{API}/payments/webhook",
        content=raw,
        headers={"Content-Type": "application/json", "X-Signature": signer.sign(raw)},
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PAYMENT_INVALID_STATE"
    assert db.scalar(select(Payment.status)) == "FAILED"
    assert _stock(db, menu) == (10, 0)
