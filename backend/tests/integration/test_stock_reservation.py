from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from app.modules.inventory.model import Inventory, StockMovement, StockReservation
from app.modules.orders.model import Order

API = "/api/v1"


def _body(menu, items):
    return {
        "customer_name": "Leo",
        "items": [{"product_id": str(menu[name]), "quantity": qty} for name, qty in items],
        "payment_method": "CASH",
    }


def _post(client, menu, items, key):
    return client.post(f"{API}/orders", json=_body(menu, items), headers={"Idempotency-Key": key})


def _stock(db, menu, name):
    """(tersedia, ditahan). Dibaca per kolom agar tidak terkena cache objek di session."""
    row = db.execute(
        select(Inventory.quantity_available, Inventory.quantity_reserved).where(
            Inventory.product_id == menu[name]
        )
    ).one()
    return tuple(row)


def _count(db, model) -> int:
    return db.scalar(select(func.count()).select_from(model))


def test_order_holds_stock_and_records_reservation_and_movement(client, menu, db):
    r = _post(client, menu, [("es_teh", 3)], "kunci-stok-001")
    assert r.status_code == 201
    order_id = r.json()["data"]["order_id"]

    assert _stock(db, menu, "es_teh") == (7, 3)  # 10 -> 7 tersedia, 3 ditahan

    reservation = db.scalars(select(StockReservation)).one()
    assert (reservation.status, reservation.quantity) == ("ACTIVE", 3)
    expires = reservation.expires_at.replace(tzinfo=None)  # SQLite membuang info zona waktu
    remaining = expires - datetime.now(UTC).replace(tzinfo=None)
    assert timedelta(minutes=6) < remaining < timedelta(minutes=8)  # bawaan 7 menit

    movement = db.scalars(select(StockMovement)).one()
    assert (movement.movement_type, movement.quantity) == ("RESERVATION", -3)
    assert str(movement.reference_id) == order_id


def test_insufficient_stock_is_rejected_with_no_side_effects(client, menu, db):
    r = _post(client, menu, [("nasi", 6)], "kunci-stok-002")  # stok nasi = 5
    assert r.status_code == 409
    error = r.json()["error"]
    assert error["code"] == "INSUFFICIENT_STOCK"
    assert error["details"][0]["requested"] == 6 and error["details"][0]["available"] == 5

    assert _stock(db, menu, "nasi") == (5, 0)
    assert _count(db, Order) == 0
    assert _count(db, StockReservation) == 0
    assert _count(db, StockMovement) == 0


def test_failed_attempt_does_not_burn_an_order_number(client, menu):
    assert _post(client, menu, [("nasi", 6)], "kunci-stok-003").status_code == 409
    ok = _post(client, menu, [("nasi", 1)], "kunci-stok-004")
    assert ok.json()["data"]["order_number"] == "A001"  # tidak melompat ke A002


def test_last_units_go_to_the_first_order_only(client, menu, db):
    assert _post(client, menu, [("nasi", 5)], "kunci-stok-005").status_code == 201
    assert _stock(db, menu, "nasi") == (0, 5)
    second = _post(client, menu, [("nasi", 1)], "kunci-stok-006")
    assert second.status_code == 409
    assert second.json()["error"]["details"][0]["available"] == 0
    assert _stock(db, menu, "nasi") == (0, 5)  # tidak pernah negatif


def test_multi_item_order_is_all_or_nothing(client, menu, db):
    r = _post(client, menu, [("es_teh", 2), ("nasi", 6)], "kunci-stok-007")
    assert r.status_code == 409
    assert _stock(db, menu, "es_teh") == (10, 0)  # pengurangan es teh ikut dibatalkan
    assert _stock(db, menu, "nasi") == (5, 0)
    assert _count(db, StockReservation) == 0


def test_out_of_stock_and_untracked_products_cannot_be_ordered(client, menu):
    for name in ("kopi", "jus"):  # kopi: stok 0; jus: tidak punya record inventory
        r = _post(client, menu, [(name, 1)], f"kunci-stok-{name}")
        assert r.status_code == 409, name
        assert r.json()["error"]["details"][0]["available"] == 0


def test_replaying_the_same_request_does_not_hold_stock_twice(client, menu, db):
    first = _post(client, menu, [("es_teh", 2)], "kunci-stok-008")
    again = _post(client, menu, [("es_teh", 2)], "kunci-stok-008")
    assert (first.status_code, again.status_code) == (201, 200)
    assert _stock(db, menu, "es_teh") == (8, 2)
    assert _count(db, StockReservation) == 1


def test_menu_reflects_held_stock(client, menu):
    for i in range(5):  # habiskan 5 porsi nasi
        assert _post(client, menu, [("nasi", 1)], f"kunci-habis-{i}").status_code == 201
    products = client.get(f"{API}/products").json()["data"]
    nasi = next(p for p in products if p["name"] == "Nasi Goreng")
    assert nasi["in_stock"] is False
