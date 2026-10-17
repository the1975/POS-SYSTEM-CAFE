import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update

from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import Order
from app.modules.orders.overdue import OrderOverdueService, build_overdue_service
from app.modules.orders.repository import OrderRepository

API = "/api/v1"


def _place(client, menu, key="kunci-overdue-001"):
    body = {
        "customer_name": "Leo",
        "items": [{"product_id": str(menu["es_teh"]), "quantity": 1}],
        "payment_method": "CASH",
    }
    r = client.post(f"{API}/orders", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 201
    return uuid.UUID(r.json()["data"]["order_id"])


def _set(db, order_id, status, minutes_ago):
    db.execute(
        update(Order)
        .where(Order.id == order_id)
        .values(status=status, ready_at=datetime.now(UTC) - timedelta(minutes=minutes_ago))
    )
    db.commit()


def _run(db) -> int:
    return build_overdue_service(db).mark_due(datetime.now(UTC))


def test_ready_order_past_threshold_becomes_overdue(client, menu, db):
    oid = _place(client, menu)
    _set(db, oid, "READY", 31)

    assert _run(db) == 1
    assert db.scalar(select(Order.status)) == "OVERDUE"
    history = db.execute(
        select(
            OrderStatusHistory.from_status,
            OrderStatusHistory.to_status,
            OrderStatusHistory.changed_by,
        ).where(OrderStatusHistory.to_status == "OVERDUE")
    ).one()
    assert tuple(history) == ("READY", "OVERDUE", None)


def test_ready_order_not_yet_due_stays_ready(client, menu, db):
    oid = _place(client, menu)
    _set(db, oid, "READY", 5)

    assert _run(db) == 0
    assert db.scalar(select(Order.status)) == "READY"


def test_only_ready_orders_are_touched(client, menu, db):
    oid = _place(client, menu)
    for status in ("PREPARING", "COMPLETED", "CANCELLED"):
        _set(db, oid, status, 120)
        assert _run(db) == 0
        assert db.scalar(select(Order.status)) == status


def test_second_run_does_nothing(client, menu, db):
    oid = _place(client, menu)
    _set(db, oid, "READY", 45)

    assert _run(db) == 1
    assert _run(db) == 0
    count = len(
        db.scalars(
            select(OrderStatusHistory).where(OrderStatusHistory.to_status == "OVERDUE")
        ).all()
    )
    assert count == 1


def test_threshold_is_configurable(client, menu, db):
    oid = _place(client, menu)
    _set(db, oid, "READY", 11)

    service = OrderOverdueService(OrderRepository(db), overdue_minutes=10)
    assert service.mark_due(datetime.now(UTC)) == 1
    assert db.scalar(select(Order.status)) == "OVERDUE"
