import uuid

import pytest
from sqlalchemy import select

from app.modules.kitchen.model import RemakeEvent
from app.modules.orders.model import Order, OrderItem
from app.modules.payments.model import Payment
from app.modules.pickup.model import Pickup
from app.modules.users.model import User

API = "/api/v1"


@pytest.fixture
def staff(staff_headers):
    return {
        "cashier": staff_headers("CASHIER", "kasir@example.com"),
        "kitchen": staff_headers("KITCHEN", "dapur@example.com"),
    }


def _paid_order(client, db, menu, staff, key, items=(("es_teh", 1), ("nasi", 1))):
    body = {
        "customer_name": "Leo",
        "items": [{"product_id": str(menu[n]), "quantity": q} for n, q in items],
        "payment_method": "CASH",
    }
    order = client.post(f"{API}/orders", json=body, headers={"Idempotency-Key": key}).json()["data"]
    pid, amount = db.execute(
        select(Payment.id, Payment.amount).where(Payment.order_id == uuid.UUID(order["order_id"]))
    ).one()
    r = client.post(
        f"{API}/payments/{pid}/cash-confirm",
        json={"cash_received": str(amount)},
        headers=staff["cashier"],
    )
    assert r.status_code == 200
    return order


def _item_ids(db, order):
    stmt = (
        select(OrderItem.id)
        .where(OrderItem.order_id == uuid.UUID(order["order_id"]))
        .order_by(OrderItem.created_at, OrderItem.id)
    )
    return db.scalars(stmt).all()


def _cooking_order(client, db, menu, staff, key, items=(("es_teh", 1), ("nasi", 1))):
    """Order dibayar, dapur sudah mulai (PREPARING). Mengembalikan (order, [id item])."""
    order = _paid_order(client, db, menu, staff, key, items)
    r = client.post(f"{API}/kitchen/orders/{order['order_id']}/start", headers=staff["kitchen"])
    assert r.status_code == 200
    return order, _item_ids(db, order)


def _ready(client, item_id, staff):
    return client.post(f"{API}/kitchen/order-items/{item_id}/ready", headers=staff["kitchen"])


def _remake(client, item_id, staff, reason="WRONG_MENU", notes=None):
    body = {"reason": reason}
    if notes is not None:
        body["notes"] = notes
    return client.post(
        f"{API}/kitchen/order-items/{item_id}/remake", json=body, headers=staff["kitchen"]
    )


def _events(db):
    return db.execute(
        select(
            RemakeEvent.order_item_id,
            RemakeEvent.reason,
            RemakeEvent.notes,
            RemakeEvent.created_by,
            RemakeEvent.resolved_at,
        )
    ).all()


def test_remake_puts_the_same_item_back_into_production(client, db, menu, staff):
    _order, (a, b) = _cooking_order(client, db, menu, staff, "kunci-remake-001")
    assert _ready(client, a, staff).status_code == 200
    kitchen_id = db.scalar(select(User.id).where(User.email == "dapur@example.com"))

    r = _remake(client, a, staff, "WRONG_MENU", "salah menu")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["status"] == "PREPARING"
    statuses = {i["order_item_id"]: i["status"] for i in data["items"]}
    assert statuses[str(a)] == "REMAKE" and statuses[str(b)] == "PREPARING"

    (event,) = _events(db)
    assert event.order_item_id == a
    assert (event.reason, event.notes) == ("WRONG_MENU", "salah menu")
    assert event.created_by == kitchen_id and event.resolved_at is None
    # bukan order/item baru
    assert len(db.execute(select(Order.id)).all()) == 1
    assert len(db.execute(select(OrderItem.id)).all()) == 2


def test_order_waits_for_the_remade_item_before_becoming_ready(client, db, menu, staff):
    _order, (a, b) = _cooking_order(client, db, menu, staff, "kunci-remake-002")
    _ready(client, a, staff)
    _remake(client, a, staff)

    only_b = _ready(client, b, staff)
    assert only_b.json()["data"]["status"] == "PREPARING"  # a belum siap lagi
    assert db.scalar(select(Order.status)) == "PREPARING"
    assert db.execute(select(Pickup.id)).all() == []

    again = _ready(client, a, staff)
    assert again.json()["data"]["status"] == "READY"
    assert len(db.execute(select(Pickup.id)).all()) == 1
    (event,) = _events(db)
    assert event.resolved_at is not None  # remake selesai saat item siap lagi


def test_item_still_cooking_can_be_remade(client, db, menu, staff):
    _order, (a, _b) = _cooking_order(client, db, menu, staff, "kunci-remake-003")
    r = _remake(client, a, staff, "CUSTOMER_REQUEST")
    assert r.status_code == 200
    statuses = {i["order_item_id"]: i["status"] for i in r.json()["data"]["items"]}
    assert statuses[str(a)] == "REMAKE"


def test_remaking_twice_in_a_row_is_rejected(client, db, menu, staff):
    _order, (a, _b) = _cooking_order(client, db, menu, staff, "kunci-remake-004")
    assert _remake(client, a, staff).status_code == 200
    again = _remake(client, a, staff)
    assert again.status_code == 409
    assert again.json()["error"]["code"] == "REMAKE_ALREADY_IN_PROGRESS"
    assert len(_events(db)) == 1


def test_same_item_can_be_remade_again_after_it_was_ready(client, db, menu, staff):
    _order, (a, _b) = _cooking_order(client, db, menu, staff, "kunci-remake-005")
    _remake(client, a, staff)
    _ready(client, a, staff)  # b belum siap, jadi order tetap PREPARING
    assert _remake(client, a, staff, "OTHER").status_code == 200
    events = _events(db)
    assert len(events) == 2
    assert sorted(e.resolved_at is None for e in events) == [False, True]


@pytest.mark.parametrize("reason", ["DAMAGED", "SPILLED", "DAMAGED_OR_SPILLED"])
def test_damaged_and_spilled_are_stored_as_the_combined_reason(client, db, menu, staff, reason):
    _order, (a, _b) = _cooking_order(client, db, menu, staff, f"kunci-remake-06-{reason}")
    assert _remake(client, a, staff, reason).status_code == 200
    (event,) = _events(db)
    assert event.reason == "DAMAGED_OR_SPILLED"


def test_unknown_or_missing_reason_is_rejected(client, db, menu, staff):
    _order, (a, _b) = _cooking_order(client, db, menu, staff, "kunci-remake-007")
    for body in ({"reason": "NGAWUR"}, {}):
        r = client.post(
            f"{API}/kitchen/order-items/{a}/remake", json=body, headers=staff["kitchen"]
        )
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "VALIDATION_ERROR"
    assert _events(db) == []


@pytest.mark.parametrize(("raw", "expected"), [("   ", None), ("  tumpah  ", "tumpah")])
def test_notes_are_trimmed_and_blank_becomes_none(client, db, menu, staff, raw, expected):
    _order, (a, _b) = _cooking_order(client, db, menu, staff, f"kunci-remake-08-{len(raw)}")
    assert _remake(client, a, staff, "OTHER", raw).status_code == 200
    (event,) = _events(db)
    assert event.notes == expected


def test_remake_before_the_order_is_started_is_rejected(client, db, menu, staff):
    order = _paid_order(client, db, menu, staff, "kunci-remake-009")
    (a, _b) = _item_ids(db, order)
    r = _remake(client, a, staff)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "KITCHEN_INVALID_STATE"
    assert _events(db) == []


def test_remake_after_the_order_is_ready_is_rejected(client, db, menu, staff):
    _order, (a, b) = _cooking_order(client, db, menu, staff, "kunci-remake-010")
    _ready(client, a, staff)
    _ready(client, b, staff)
    assert db.scalar(select(Order.status)) == "READY"
    r = _remake(client, a, staff)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "KITCHEN_INVALID_STATE"
    assert db.scalar(select(Order.status)) == "READY"
    assert _events(db) == []


def test_unknown_item_returns_404(client, staff):
    r = _remake(client, uuid.uuid4(), staff)
    assert (r.status_code, r.json()["error"]["code"]) == (404, "ORDER_ITEM_NOT_FOUND")


def test_remake_requires_login(client):
    r = client.post(f"{API}/kitchen/order-items/{uuid.uuid4()}/remake", json={"reason": "OTHER"})
    assert r.status_code == 401


@pytest.mark.parametrize("role", ["CASHIER", "PICKUP"])
def test_other_roles_cannot_remake(client, staff_headers, role):
    r = client.post(
        f"{API}/kitchen/order-items/{uuid.uuid4()}/remake",
        json={"reason": "OTHER"},
        headers=staff_headers(role),
    )
    assert r.status_code == 403


@pytest.mark.parametrize("role", ["KITCHEN", "CONTROLLER", "ADMIN"])
def test_kitchen_roles_pass_authorization(client, staff_headers, role):
    # 404 (bukan 403) membuktikan otorisasi lolos dan baru gagal karena itemnya tidak ada.
    r = client.post(
        f"{API}/kitchen/order-items/{uuid.uuid4()}/remake",
        json={"reason": "OTHER"},
        headers=staff_headers(role),
    )
    assert r.status_code == 404
