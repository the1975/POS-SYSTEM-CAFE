from sqlalchemy import select, update

from app.modules.audit.model import AuditLog
from app.modules.inventory.model import Inventory, StockMovement
from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import Order
from app.modules.payments.model import Payment

API = "/api/v1"


def _paid_cash_order(client, db, menu, staff_headers, *, confirm=True):
    body = {
        "customer_name": "Leo",
        "items": [{"product_id": str(menu["es_teh"]), "quantity": 2}],
        "payment_method": "CASH",
    }
    r = client.post(f"{API}/orders", json=body, headers={"Idempotency-Key": "kunci-refund-001"})
    assert r.status_code == 201
    pid, amount = db.execute(select(Payment.id, Payment.amount)).one()
    if confirm:
        r = client.post(
            f"{API}/payments/{pid}/cash-confirm",
            json={"cash_received": str(amount)},
            headers=staff_headers("CASHIER"),
        )
        assert r.status_code == 200
    return pid, amount


def _refund(client, pid, amount, headers=None, reason="Menu habis"):
    return client.post(
        f"{API}/payments/{pid}/refund",
        json={"amount": str(amount), "reason": reason},
        headers=headers or {},
    )


def _stock(db, menu):
    row = db.execute(
        select(Inventory.quantity_available, Inventory.quantity_reserved).where(
            Inventory.product_id == menu["es_teh"]
        )
    ).one()
    return tuple(row)


def test_admin_refunds_cash_order_and_stock_returns(client, db, menu, staff_headers):
    pid, amount = _paid_cash_order(client, db, menu, staff_headers)
    assert _stock(db, menu) == (8, 0)

    r = _refund(client, pid, amount, staff_headers("ADMIN"))
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert (data["payment_status"], data["order_status"]) == ("REFUNDED", "CANCELLED")

    assert db.scalar(select(Payment.status)) == "REFUNDED"
    assert db.scalar(select(Order.status)) == "CANCELLED"
    assert _stock(db, menu) == (10, 0)

    movement = db.execute(
        select(StockMovement.movement_type, StockMovement.quantity).where(
            StockMovement.movement_type == "RESTOCK"
        )
    ).one()
    assert tuple(movement) == ("RESTOCK", 2)

    history = db.execute(
        select(OrderStatusHistory.from_status, OrderStatusHistory.to_status).where(
            OrderStatusHistory.to_status == "CANCELLED"
        )
    ).one()
    assert tuple(history) == ("CONFIRMED", "CANCELLED")

    audit = db.scalars(select(AuditLog)).one()
    assert audit.action == "REFUND_PAYMENT" and audit.entity_id == pid
    assert audit.old_value == {"status": "PAID"}
    assert audit.new_value["status"] == "REFUNDED"
    assert audit.new_value["reason"] == "Menu habis"


def test_cashier_cannot_refund(client, db, menu, staff_headers):
    pid, amount = _paid_cash_order(client, db, menu, staff_headers)
    r = _refund(client, pid, amount, staff_headers("CASHIER", "kasir-lain@example.com"))
    assert r.status_code == 403
    assert db.scalar(select(Payment.status)) == "PAID"


def test_refund_requires_login(client, db, menu, staff_headers):
    pid, amount = _paid_cash_order(client, db, menu, staff_headers)
    assert _refund(client, pid, amount).status_code == 401


def test_partial_amount_rejected(client, db, menu, staff_headers):
    pid, amount = _paid_cash_order(client, db, menu, staff_headers)
    r = _refund(client, pid, amount - 1000, staff_headers("ADMIN"))
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "REFUND_AMOUNT_INVALID"
    assert db.scalar(select(Payment.status)) == "PAID"


def test_unpaid_payment_cannot_be_refunded(client, db, menu, staff_headers):
    pid, amount = _paid_cash_order(client, db, menu, staff_headers, confirm=False)
    r = _refund(client, pid, amount, staff_headers("ADMIN"))
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "REFUND_NOT_ALLOWED"


def test_double_refund_rejected_and_stock_not_doubled(client, db, menu, staff_headers):
    pid, amount = _paid_cash_order(client, db, menu, staff_headers)
    admin = staff_headers("ADMIN")
    assert _refund(client, pid, amount, admin).status_code == 200
    r = _refund(client, pid, amount, admin)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "REFUND_NOT_ALLOWED"
    assert _stock(db, menu) == (10, 0)
    assert len(db.scalars(select(AuditLog)).all()) == 1


def test_order_already_preparing_rejected(client, db, menu, staff_headers):
    pid, amount = _paid_cash_order(client, db, menu, staff_headers)
    db.execute(update(Order).values(status="PREPARING"))
    db.commit()
    r = _refund(client, pid, amount, staff_headers("ADMIN"))
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "REFUND_NOT_ALLOWED"
    assert db.scalar(select(Payment.status)) == "PAID"
    assert _stock(db, menu) == (8, 0)


def test_qris_refund_not_supported_yet(client, db, menu, staff_headers):
    pid, amount = _paid_cash_order(client, db, menu, staff_headers)
    db.execute(update(Payment).values(payment_method="QRIS"))
    db.commit()
    r = _refund(client, pid, amount, staff_headers("ADMIN"))
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "REFUND_NOT_ALLOWED"


def test_reason_required(client, db, menu, staff_headers):
    pid, amount = _paid_cash_order(client, db, menu, staff_headers)
    r = _refund(client, pid, amount, staff_headers("ADMIN"), reason="  ")
    assert r.status_code == 422
