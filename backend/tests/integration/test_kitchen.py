import uuid

import pytest
from sqlalchemy import select, update

from app.core.security import derive_pickup_token, derive_tracking_token, hash_token
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import Order, OrderItem
from app.modules.payments.model import Payment
from app.modules.pickup.model import Pickup
from app.modules.users.model import User

API = "/api/v1"


def _place(client, menu, key, items=(("es_teh", 1),)):
    body = {
        "customer_name": "Leo",
        "items": [{"product_id": str(menu[n]), "quantity": q} for n, q in items],
        "payment_method": "CASH",
    }
    r = client.post(f"{API}/orders", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 201
    return r.json()["data"]


def _confirmed(client, db, menu, cashier, key, items=(("es_teh", 1),)):
    """Order yang sudah dibayar kasir (status CONFIRMED), siap masuk antrean dapur."""
    order = _place(client, menu, key, items)
    pid, amount = db.execute(
        select(Payment.id, Payment.amount).where(Payment.order_id == uuid.UUID(order["order_id"]))
    ).one()
    r = client.post(
        f"{API}/payments/{pid}/cash-confirm", json={"cash_received": str(amount)}, headers=cashier
    )
    assert r.status_code == 200
    return order


def _start(client, order, headers):
    return client.post(f"{API}/kitchen/orders/{order['order_id']}/start", headers=headers)


def _ready(client, item_id, headers):
    return client.post(f"{API}/kitchen/order-items/{item_id}/ready", headers=headers)


def _item_ids(db, order):
    stmt = select(OrderItem.id).where(OrderItem.order_id == uuid.UUID(order["order_id"]))
    return [row[0] for row in db.execute(stmt)]


def _item_statuses(db):
    return set(db.scalars(select(OrderItem.status)))


def _history(db, to_status):
    return db.execute(
        select(OrderStatusHistory.changed_by).where(OrderStatusHistory.to_status == to_status)
    ).all()


def test_queue_lists_paid_orders_oldest_first_with_items(client, db, menu, staff_headers):
    cashier = staff_headers("CASHIER", "kasir@example.com")
    kitchen = staff_headers("KITCHEN", "dapur@example.com")
    first = _confirmed(client, db, menu, cashier, "kunci-dapur-001", (("es_teh", 1), ("nasi", 1)))
    second = _confirmed(client, db, menu, cashier, "kunci-dapur-002")
    _place(client, menu, "kunci-dapur-003")  # belum dibayar: tidak boleh masuk antrean dapur

    r = client.get(f"{API}/kitchen/orders", headers=kitchen)
    assert r.status_code == 200
    body = r.json()
    assert body["pagination"]["total"] == 2
    assert [o["order_number"] for o in body["data"]] == [
        first["order_number"],
        second["order_number"],
    ]
    assert len(body["data"][0]["items"]) == 2
    assert {i["status"] for o in body["data"] for i in o["items"]} == {"PENDING"}
    assert "tracking_token" not in r.text


def test_status_filter(client, db, menu, staff_headers):
    cashier = staff_headers("CASHIER", "kasir@example.com")
    kitchen = staff_headers("KITCHEN", "dapur@example.com")
    first = _confirmed(client, db, menu, cashier, "kunci-dapur-010")
    _confirmed(client, db, menu, cashier, "kunci-dapur-011")
    assert _start(client, first, kitchen).status_code == 200

    def total(status):
        r = client.get(f"{API}/kitchen/orders", params={"status": status}, headers=kitchen)
        return r.json()["pagination"]["total"]

    assert (total("PREPARING"), total("CONFIRMED"), total("READY")) == (1, 1, 0)


def test_start_moves_order_and_items_to_preparing(client, db, menu, staff_headers):
    cashier = staff_headers("CASHIER", "kasir@example.com")
    kitchen = staff_headers("KITCHEN", "dapur@example.com")
    order = _confirmed(client, db, menu, cashier, "kunci-dapur-020", (("es_teh", 1), ("nasi", 1)))
    kitchen_id = db.scalar(select(User.id).where(User.email == "dapur@example.com"))

    r = _start(client, order, kitchen)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["status"] == "PREPARING"
    assert {i["status"] for i in data["items"]} == {"PREPARING"}

    status, preparing_at = db.execute(select(Order.status, Order.preparing_at)).one()
    assert status == "PREPARING" and preparing_at is not None
    assert _item_statuses(db) == {"PREPARING"}
    assert _history(db, "PREPARING") == [(kitchen_id,)]


def test_starting_twice_is_harmless(client, db, menu, staff_headers):
    cashier = staff_headers("CASHIER", "kasir@example.com")
    kitchen = staff_headers("KITCHEN", "dapur@example.com")
    order = _confirmed(client, db, menu, cashier, "kunci-dapur-021")
    assert _start(client, order, kitchen).status_code == 200
    again = _start(client, order, kitchen)
    assert again.status_code == 200 and again.json()["data"]["status"] == "PREPARING"
    assert len(_history(db, "PREPARING")) == 1


def test_unpaid_order_cannot_be_started(client, db, menu, staff_headers):
    kitchen = staff_headers("KITCHEN", "dapur@example.com")
    order = _place(client, menu, "kunci-dapur-022")
    r = _start(client, order, kitchen)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "KITCHEN_INVALID_STATE"
    assert db.scalar(select(Order.status)) == "PENDING"


def test_start_checks_payment_is_really_paid(client, db, menu, staff_headers):
    cashier = staff_headers("CASHIER", "kasir@example.com")
    kitchen = staff_headers("KITCHEN", "dapur@example.com")
    order = _confirmed(client, db, menu, cashier, "kunci-dapur-023")
    db.execute(update(Payment).values(status="FAILED"))
    db.commit()
    r = _start(client, order, kitchen)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "ORDER_NOT_PAID"
    assert db.scalar(select(Order.status)) == "CONFIRMED"


def test_order_becomes_ready_only_when_every_item_is_ready(client, db, menu, staff_headers):
    cashier = staff_headers("CASHIER", "kasir@example.com")
    kitchen = staff_headers("KITCHEN", "dapur@example.com")
    order = _confirmed(client, db, menu, cashier, "kunci-dapur-030", (("es_teh", 1), ("nasi", 1)))
    kitchen_id = db.scalar(select(User.id).where(User.email == "dapur@example.com"))
    _start(client, order, kitchen)
    first_item, last_item = _item_ids(db, order)

    one = _ready(client, first_item, kitchen)
    assert one.status_code == 200 and one.json()["data"]["status"] == "PREPARING"
    assert db.scalar(select(Order.status)) == "PREPARING"
    assert db.execute(select(Pickup.id)).all() == []  # belum ada pickup

    last = _ready(client, last_item, kitchen)
    assert last.status_code == 200 and last.json()["data"]["status"] == "READY"
    status, ready_at = db.execute(select(Order.status, Order.ready_at)).one()
    assert status == "READY" and ready_at is not None
    assert _history(db, "READY") == [(kitchen_id,)]

    pickup = db.execute(select(Pickup.status, Pickup.pickup_token_hash)).one()
    order_id = uuid.UUID(order["order_id"])
    assert pickup.status == "WAITING_PICKUP"
    assert pickup.pickup_token_hash == hash_token(derive_pickup_token(order_id))
    # token tracking customer TIDAK boleh sama dengan token pickup
    assert pickup.pickup_token_hash != hash_token(derive_tracking_token(order_id))

    detail = client.get(
        f"{API}/orders/{order['order_id']}", headers={"X-Tracking-Token": order["tracking_token"]}
    ).json()["data"]
    assert detail["status"] == "READY"


def test_marking_ready_twice_is_harmless(client, db, menu, staff_headers):
    cashier = staff_headers("CASHIER", "kasir@example.com")
    kitchen = staff_headers("KITCHEN", "dapur@example.com")
    order = _confirmed(client, db, menu, cashier, "kunci-dapur-031")
    _start(client, order, kitchen)
    (item,) = _item_ids(db, order)
    assert _ready(client, item, kitchen).status_code == 200
    again = _ready(client, item, kitchen)
    assert again.status_code == 200 and again.json()["data"]["status"] == "READY"
    assert len(db.execute(select(Pickup.id)).all()) == 1
    assert len(_history(db, "READY")) == 1


def test_item_cannot_be_ready_before_order_is_started(client, db, menu, staff_headers):
    cashier = staff_headers("CASHIER", "kasir@example.com")
    kitchen = staff_headers("KITCHEN", "dapur@example.com")
    order = _confirmed(client, db, menu, cashier, "kunci-dapur-032")
    (item,) = _item_ids(db, order)
    r = _ready(client, item, kitchen)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "KITCHEN_INVALID_STATE"
    assert _item_statuses(db) == {"PENDING"}


def test_unknown_order_and_item_return_404(client, staff_headers):
    kitchen = staff_headers("KITCHEN", "dapur@example.com")
    r1 = client.post(f"{API}/kitchen/orders/{uuid.uuid4()}/start", headers=kitchen)
    assert (r1.status_code, r1.json()["error"]["code"]) == (404, "ORDER_NOT_FOUND")
    r2 = _ready(client, uuid.uuid4(), kitchen)
    assert (r2.status_code, r2.json()["error"]["code"]) == (404, "ORDER_ITEM_NOT_FOUND")


def test_kitchen_requires_login(client):
    assert client.get(f"{API}/kitchen/orders").status_code == 401


@pytest.mark.parametrize("role", ["CASHIER", "PICKUP"])
def test_other_roles_cannot_use_kitchen(client, staff_headers, role):
    assert client.get(f"{API}/kitchen/orders", headers=staff_headers(role)).status_code == 403


@pytest.mark.parametrize("role", ["KITCHEN", "CONTROLLER", "ADMIN"])
def test_kitchen_roles_can_see_the_queue(client, staff_headers, role):
    assert client.get(f"{API}/kitchen/orders", headers=staff_headers(role)).status_code == 200


def test_queue_pagination(client, db, menu, staff_headers):
    cashier = staff_headers("CASHIER", "kasir@example.com")
    kitchen = staff_headers("KITCHEN", "dapur@example.com")
    for i in range(3):
        _confirmed(client, db, menu, cashier, f"kunci-dapur-04{i}")
    page1 = client.get(
        f"{API}/kitchen/orders", params={"page": 1, "page_size": 2}, headers=kitchen
    ).json()
    assert len(page1["data"]) == 2
    assert (page1["pagination"]["total"], page1["pagination"]["total_pages"]) == (3, 2)
    page2 = client.get(
        f"{API}/kitchen/orders", params={"page": 2, "page_size": 2}, headers=kitchen
    ).json()
    assert len(page2["data"]) == 1
