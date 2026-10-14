from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select, update

from app.core.security import hash_password
from app.modules.inventory.model import Inventory, StockMovement, StockReservation
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import Order
from app.modules.payments.model import Payment
from app.modules.users.model import Role, User

API = "/api/v1"
PASSWORD = "password-uji-12345"


def _make_user(db, role_name, email) -> User:
    role = db.scalar(select(Role).where(Role.name == role_name))
    if role is None:
        role = Role(name=role_name)
        db.add(role)
        db.flush()
    user = User(
        role_id=role.id,
        name=f"Staf {role_name}",
        email=email,
        password_hash=hash_password(PASSWORD),
    )
    db.add(user)
    db.commit()
    return user


def _headers(client, email) -> dict:
    r = client.post(f"{API}/auth/login", json={"email": email, "password": PASSWORD})
    return {"Authorization": f"Bearer {r.json()['data']['access_token']}"}


def _place_order(client, menu, key, method="CASH", items=(("es_teh", 2),)):
    body = {
        "customer_name": "Leo",
        "items": [{"product_id": str(menu[n]), "quantity": q} for n, q in items],
        "payment_method": method,
    }
    r = client.post(f"{API}/orders", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 201


def _payment(db):
    row = db.execute(select(Payment.id, Payment.amount)).one()
    return row.id, row.amount


def _confirm(client, payment_id, cash, headers):
    return client.post(
        f"{API}/payments/{payment_id}/cash-confirm",
        json={"cash_received": str(cash)},
        headers=headers,
    )


def _stock(db, menu, name="es_teh"):
    row = db.execute(
        select(Inventory.quantity_available, Inventory.quantity_reserved).where(
            Inventory.product_id == menu[name]
        )
    ).one()
    return tuple(row)


def test_cashier_confirms_payment_and_order_becomes_confirmed(client, menu, db):
    cashier = _make_user(db, "CASHIER", "kasir@example.com")
    _place_order(client, menu, "kunci-kasir-001")
    pid, amount = _payment(db)

    r = _confirm(client, pid, amount + Decimal(5000), _headers(client, "kasir@example.com"))
    assert r.status_code == 200
    data = r.json()["data"]
    assert (data["payment_status"], data["order_status"]) == ("PAID", "CONFIRMED")
    assert Decimal(str(data["change"])) == Decimal(5000)

    status, cash, change, paid_at = db.execute(
        select(Payment.status, Payment.cash_received, Payment.change_amount, Payment.paid_at)
    ).one()
    assert status == "PAID" and paid_at is not None
    assert cash == amount + 5000 and change == 5000

    order_status, confirmed_at = db.execute(select(Order.status, Order.confirmed_at)).one()
    assert order_status == "CONFIRMED" and confirmed_at is not None

    assert db.scalar(select(StockReservation.status)) == "CONVERTED"
    assert _stock(db, menu) == (8, 0)  # 10 -> 8 tersedia; yang ditahan sudah terjual
    movements = [
        tuple(m) for m in db.execute(select(StockMovement.movement_type, StockMovement.quantity))
    ]
    assert sorted(movements) == [("RESERVATION", -2), ("SALE", -2)]

    to_statuses = set(db.scalars(select(OrderStatusHistory.to_status)))
    assert to_statuses == {"PENDING", "CONFIRMED"}
    confirmed_by = db.scalar(
        select(OrderStatusHistory.changed_by).where(OrderStatusHistory.to_status == "CONFIRMED")
    )
    assert confirmed_by == cashier.id


def test_insufficient_cash_is_rejected_and_nothing_changes(client, menu, db):
    _make_user(db, "CASHIER", "kasir@example.com")
    _place_order(client, menu, "kunci-kasir-002")
    pid, amount = _payment(db)

    r = _confirm(client, pid, amount - Decimal(1), _headers(client, "kasir@example.com"))
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INSUFFICIENT_CASH"
    assert db.scalar(select(Payment.status)) == "WAITING_CASH"
    assert db.scalar(select(Order.status)) == "PENDING"
    assert db.scalar(select(StockReservation.status)) == "ACTIVE"
    assert _stock(db, menu) == (8, 2)


def test_confirming_twice_is_rejected_and_stock_is_not_sold_twice(client, menu, db):
    _make_user(db, "CASHIER", "kasir@example.com")
    _place_order(client, menu, "kunci-kasir-003")
    pid, amount = _payment(db)
    headers = _headers(client, "kasir@example.com")

    assert _confirm(client, pid, amount, headers).status_code == 200
    again = _confirm(client, pid, amount, headers)
    assert again.status_code == 409
    assert again.json()["error"]["code"] == "PAYMENT_ALREADY_PAID"
    assert _stock(db, menu) == (8, 0)
    sales = [m for m in db.scalars(select(StockMovement.movement_type)) if m == "SALE"]
    assert len(sales) == 1


def test_cash_confirm_requires_login(client):
    r = client.post(f"{API}/payments/{uuid4()}/cash-confirm", json={"cash_received": "1000"})
    assert r.status_code == 401


def test_other_roles_cannot_confirm_cash(client, db):
    _make_user(db, "KITCHEN", "dapur@example.com")
    r = _confirm(client, uuid4(), 1000, _headers(client, "dapur@example.com"))
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "FORBIDDEN"


def test_admin_can_also_confirm_cash(client, menu, db):
    _make_user(db, "ADMIN", "admin@example.com")
    _place_order(client, menu, "kunci-kasir-004")
    pid, amount = _payment(db)
    assert _confirm(client, pid, amount, _headers(client, "admin@example.com")).status_code == 200


def test_unknown_payment_returns_404(client, db):
    _make_user(db, "CASHIER", "kasir@example.com")
    r = _confirm(client, uuid4(), 1000, _headers(client, "kasir@example.com"))
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "PAYMENT_NOT_FOUND"


def test_qris_payment_cannot_be_confirmed_as_cash(client, menu, db):
    _make_user(db, "CASHIER", "kasir@example.com")
    _place_order(client, menu, "kunci-kasir-005", method="QRIS")
    pid, amount = _payment(db)
    r = _confirm(client, pid, amount, _headers(client, "kasir@example.com"))
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PAYMENT_NOT_CASH"


@pytest.mark.parametrize("cash", ["0", "-5"])
def test_cash_received_must_be_positive(client, db, cash):
    _make_user(db, "CASHIER", "kasir@example.com")
    r = _confirm(client, uuid4(), cash, _headers(client, "kasir@example.com"))
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"


def test_inactive_reservation_blocks_confirmation_and_rolls_back(client, menu, db):
    _make_user(db, "CASHIER", "kasir@example.com")
    _place_order(client, menu, "kunci-kasir-006")
    pid, amount = _payment(db)
    db.execute(update(StockReservation).values(status="EXPIRED"))
    db.commit()

    r = _confirm(client, pid, amount, _headers(client, "kasir@example.com"))
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "RESERVATION_NOT_ACTIVE"
    # Payment sempat di-update lalu dibatalkan: harus kembali seperti semula.
    assert db.scalar(select(Payment.status)) == "WAITING_CASH"
    assert db.scalar(select(Order.status)) == "PENDING"
