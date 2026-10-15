import uuid

import pytest
from sqlalchemy import select, update

from app.modules.orders.history_model import OrderStatusHistory
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
        "pickup": staff_headers("PICKUP", "pickup@example.com"),
    }


def _paid_order(client, db, menu, staff, key, items=(("es_teh", 1),)):
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


def _cook(client, db, staff, order):
    start = client.post(f"{API}/kitchen/orders/{order['order_id']}/start", headers=staff["kitchen"])
    assert start.status_code == 200
    item_ids = db.scalars(
        select(OrderItem.id).where(OrderItem.order_id == uuid.UUID(order["order_id"]))
    ).all()
    for item_id in item_ids:
        r = client.post(f"{API}/kitchen/order-items/{item_id}/ready", headers=staff["kitchen"])
        assert r.status_code == 200


def _ready_order(client, db, menu, staff, key, items=(("es_teh", 1),)):
    order = _paid_order(client, db, menu, staff, key, items)
    _cook(client, db, staff, order)
    return order


def _detail(client, order):
    r = client.get(
        f"{API}/orders/{order['order_id']}", headers={"X-Tracking-Token": order["tracking_token"]}
    )
    return r.json()["data"]


def _pickup_token(client, order):
    return _detail(client, order)["pickup_token"]


def _pickup_id(db, order):
    return db.scalar(select(Pickup.id).where(Pickup.order_id == uuid.UUID(order["order_id"])))


def _verify(client, token, staff):
    return client.post(
        f"{API}/pickup/verify", json={"pickup_token": token}, headers=staff["pickup"]
    )


def _complete(client, pickup_id, staff):
    return client.post(f"{API}/pickup/{pickup_id}/complete", headers=staff["pickup"])


def test_customer_sees_pickup_token_only_while_waiting(client, db, menu, staff):
    order = _paid_order(client, db, menu, staff, "kunci-ambil-001")
    assert _pickup_token(client, order) is None  # CONFIRMED: belum siap

    _cook(client, db, staff, order)
    token = _pickup_token(client, order)
    assert token and token != order["tracking_token"]

    assert _verify(client, token, staff).status_code == 200
    assert _complete(client, _pickup_id(db, order), staff).status_code == 200
    detail = _detail(client, order)
    assert detail["status"] == "COMPLETED" and detail["pickup_token"] is None


def test_list_shows_ready_orders_with_items_and_no_tokens(client, db, menu, staff):
    first = _ready_order(client, db, menu, staff, "kunci-ambil-010", (("es_teh", 2), ("nasi", 1)))
    _ready_order(client, db, menu, staff, "kunci-ambil-011")
    _paid_order(client, db, menu, staff, "kunci-ambil-012")  # belum dimasak: tidak muncul

    r = client.get(f"{API}/pickup/orders", headers=staff["pickup"])
    assert r.status_code == 200
    body = r.json()
    assert body["pagination"]["total"] == 2
    row = next(o for o in body["data"] if o["order_number"] == first["order_number"])
    assert row["pickup_id"] == str(_pickup_id(db, first))
    assert row["verified"] is False and row["status"] == "READY"
    assert {i["name"] for i in row["items"]} == {"Es Teh", "Nasi Goreng"}
    assert first["tracking_token"] not in r.text
    assert _pickup_token(client, first) not in r.text


def test_verify_returns_summary_and_records_who_verified(client, db, menu, staff):
    order = _ready_order(client, db, menu, staff, "kunci-ambil-020", (("es_teh", 2),))
    token = _pickup_token(client, order)
    pickup_user = db.scalar(select(User.id).where(User.email == "pickup@example.com"))

    r = _verify(client, token, staff)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["pickup_id"] == str(_pickup_id(db, order))
    assert data["order_number"] == order["order_number"]
    assert (data["customer_name"], data["status"], data["payment_status"]) == (
        "Leo",
        "READY",
        "PAID",
    )
    assert [(i["name"], i["quantity"]) for i in data["items"]] == [("Es Teh", 2)]

    status, verified_by, verified_at = db.execute(
        select(Pickup.status, Pickup.verified_by, Pickup.verified_at)
    ).one()
    assert status == "WAITING_PICKUP"  # verifikasi belum menyelesaikan pickup
    assert verified_by == pickup_user and verified_at is not None
    assert db.scalar(select(Order.status)) == "READY"


def test_wrong_token_and_tracking_token_are_rejected(client, db, menu, staff):
    order = _ready_order(client, db, menu, staff, "kunci-ambil-030")
    for token in ("token-ngawur-sekali", order["tracking_token"]):
        r = _verify(client, token, staff)
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "PICKUP_NOT_FOUND"
    assert db.scalar(select(Pickup.verified_at)) is None


def test_complete_after_verify_finishes_pickup_and_order(client, db, menu, staff):
    order = _ready_order(client, db, menu, staff, "kunci-ambil-040")
    pickup_user = db.scalar(select(User.id).where(User.email == "pickup@example.com"))
    _verify(client, _pickup_token(client, order), staff)

    r = _complete(client, _pickup_id(db, order), staff)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["order_number"] == order["order_number"] and data["status"] == "COMPLETED"

    pickup_status, pickup_done = db.execute(select(Pickup.status, Pickup.completed_at)).one()
    assert pickup_status == "COMPLETED" and pickup_done is not None
    order_status, completed_at = db.execute(select(Order.status, Order.completed_at)).one()
    assert order_status == "COMPLETED" and completed_at is not None
    history = db.execute(
        select(OrderStatusHistory.from_status, OrderStatusHistory.changed_by).where(
            OrderStatusHistory.to_status == "COMPLETED"
        )
    ).all()
    assert [tuple(h) for h in history] == [("READY", pickup_user)]


def test_complete_requires_verification(client, db, menu, staff):
    order = _ready_order(client, db, menu, staff, "kunci-ambil-050")
    r = _complete(client, _pickup_id(db, order), staff)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PICKUP_NOT_VERIFIED"
    assert db.scalar(select(Order.status)) == "READY"
    assert db.scalar(select(Pickup.status)) == "WAITING_PICKUP"


def test_completing_twice_is_rejected(client, db, menu, staff):
    order = _ready_order(client, db, menu, staff, "kunci-ambil-060")
    _verify(client, _pickup_token(client, order), staff)
    pid = _pickup_id(db, order)
    assert _complete(client, pid, staff).status_code == 200
    again = _complete(client, pid, staff)
    assert again.status_code == 409
    assert again.json()["error"]["code"] == "PICKUP_ALREADY_COMPLETED"
    done = db.execute(
        select(OrderStatusHistory.id).where(OrderStatusHistory.to_status == "COMPLETED")
    ).all()
    assert len(done) == 1


def test_verifying_after_completion_is_rejected(client, db, menu, staff):
    order = _ready_order(client, db, menu, staff, "kunci-ambil-070")
    token = _pickup_token(client, order)
    _verify(client, token, staff)
    _complete(client, _pickup_id(db, order), staff)
    r = _verify(client, token, staff)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PICKUP_ALREADY_COMPLETED"


def test_overdue_order_can_still_be_picked_up(client, db, menu, staff):
    order = _ready_order(client, db, menu, staff, "kunci-ambil-080")
    token = _pickup_token(client, order)
    db.execute(update(Order).values(status="OVERDUE"))
    db.commit()
    assert _pickup_token(client, order) == token  # token tetap terlihat customer
    assert _verify(client, token, staff).status_code == 200
    assert _complete(client, _pickup_id(db, order), staff).status_code == 200
    assert db.scalar(select(Order.status)) == "COMPLETED"
    from_status = db.scalar(
        select(OrderStatusHistory.from_status).where(OrderStatusHistory.to_status == "COMPLETED")
    )
    assert from_status == "OVERDUE"


def test_order_in_a_wrong_state_blocks_pickup(client, db, menu, staff):
    order = _ready_order(client, db, menu, staff, "kunci-ambil-090")
    token = _pickup_token(client, order)
    db.execute(update(Order).values(status="CANCELLED"))
    db.commit()
    r = _verify(client, token, staff)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PICKUP_INVALID_STATE"
    assert db.scalar(select(Pickup.verified_at)) is None
    assert _pickup_token(client, order) is None  # order batal: token tidak ditampilkan lagi


def test_unknown_pickup_returns_404(client, staff):
    r = _complete(client, uuid.uuid4(), staff)
    assert (r.status_code, r.json()["error"]["code"]) == (404, "PICKUP_NOT_FOUND")


def test_pickup_requires_login(client):
    assert client.get(f"{API}/pickup/orders").status_code == 401


def test_verify_input_is_validated(client, staff):
    for body in ({}, {"pickup_token": "pendek"}):
        r = client.post(f"{API}/pickup/verify", json=body, headers=staff["pickup"])
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize("role", ["CASHIER", "KITCHEN"])
def test_other_roles_cannot_use_pickup(client, staff_headers, role):
    assert client.get(f"{API}/pickup/orders", headers=staff_headers(role)).status_code == 403


@pytest.mark.parametrize("role", ["PICKUP", "CONTROLLER", "ADMIN"])
def test_pickup_roles_can_list(client, staff_headers, role):
    assert client.get(f"{API}/pickup/orders", headers=staff_headers(role)).status_code == 200
