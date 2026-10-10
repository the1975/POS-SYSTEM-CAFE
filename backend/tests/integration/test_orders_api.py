import hashlib
from decimal import Decimal

from sqlalchemy import func, select

from app.modules.orders.history_model import OrderStatusHistory
from app.modules.orders.model import Order, OrderItem
from app.modules.products.model import Product

API = "/api/v1"
KEY = "kunci-test-0001"


def _body(menu, items=None, **override):
    body = {
        "customer_name": "Leonardo",
        "items": items
        or [
            {"product_id": str(menu["es_teh"]), "quantity": 2},
            {"product_id": str(menu["nasi"]), "quantity": 1},
        ],
        "payment_method": "QRIS",
    }
    body.update(override)
    return body


def _post(client, body, key=KEY):
    headers = {"Idempotency-Key": key} if key else {}
    return client.post(f"{API}/orders", json=body, headers=headers)


def _count_orders(db) -> int:
    return db.scalar(select(func.count()).select_from(Order))


# ---- pembuatan order -------------------------------------------------------------------
def test_create_order_calculates_totals_on_the_server(client, menu):
    r = _post(client, _body(menu))
    assert r.status_code == 201
    d = r.json()["data"]
    # 2 x 8.000 + 1 x 25.000 = 41.000; pajak 10% = 4.100; total 45.100
    assert (d["subtotal"], d["discount_amount"], d["tax_amount"], d["total"]) == (
        41000, 0, 4100, 45100,
    )
    assert d["status"] == "PENDING"
    assert d["order_number"] == "A001"
    assert d["customer_name"] == "Leonardo"
    assert len(d["tracking_token"]) >= 43


def test_order_numbers_increase(client, menu):
    first = _post(client, _body(menu), key="kunci-test-0001").json()["data"]
    second = _post(client, _body(menu), key="kunci-test-0002").json()["data"]
    assert (first["order_number"], second["order_number"]) == ("A001", "A002")


def test_client_cannot_send_price_or_total(client, menu):
    r = _post(client, _body(menu, total=1))
    assert r.status_code == 422
    items = [{"product_id": str(menu["es_teh"]), "quantity": 1, "price": 1}]
    assert _post(client, _body(menu, items=items)).status_code == 422


def test_invalid_input_is_rejected(client, menu):
    one = {"product_id": str(menu["es_teh"]), "quantity": 1}
    cases = [
        _body(menu, items=[]),  # keranjang kosong
        _body(menu, items=[{**one, "quantity": 0}]),  # jumlah 0
        _body(menu, items=[{**one, "quantity": -3}]),  # jumlah negatif
        _body(menu, customer_name="   "),  # nama kosong
        _body(menu, payment_method="BITCOIN"),  # metode tidak dikenal
    ]
    for body in cases:
        assert _post(client, body).status_code == 422, body


def test_quantity_above_limit_is_rejected(client, menu):
    items = [{"product_id": str(menu["es_teh"]), "quantity": 21}]  # batas bawaan 20
    r = _post(client, _body(menu, items=items))
    assert r.status_code == 422
    assert r.json()["error"]["details"][0]["reason"] == "QUANTITY_EXCEEDS_LIMIT"


def test_unknown_unavailable_or_hidden_products_are_rejected(client, menu, db):
    import uuid

    for pid in (uuid.uuid4(), menu["mie"], menu["rahasia"]):
        r = _post(client, _body(menu, items=[{"product_id": str(pid), "quantity": 1}]))
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "INVALID_ORDER_ITEMS"
    assert _count_orders(db) == 0  # tidak ada order setengah jadi


def test_duplicate_product_lines_are_merged(client, menu, db):
    es = str(menu["es_teh"])
    items = [{"product_id": es, "quantity": 2}, {"product_id": es, "quantity": 3}]
    r = _post(client, _body(menu, items=items))
    assert r.status_code == 201
    assert r.json()["data"]["subtotal"] == 40000  # 5 x 8.000
    rows = db.scalars(select(OrderItem)).all()
    assert len(rows) == 1 and rows[0].quantity == 5


def test_history_row_created_with_order(client, menu, db):
    _post(client, _body(menu))
    history = db.scalars(select(OrderStatusHistory)).one()
    assert history.from_status is None and history.to_status == "PENDING"


# ---- snapshot & token ------------------------------------------------------------------
def test_items_keep_name_and_price_snapshot(client, menu, db):
    _post(client, _body(menu))
    product = db.get(Product, menu["es_teh"])
    product.price = Decimal(9999)  # admin mengubah harga setelah order dibuat
    product.name = "Es Teh Jumbo"
    db.commit()
    row = db.scalars(
        select(OrderItem).where(OrderItem.product_id == menu["es_teh"])
    ).one()
    assert row.product_name_snapshot == "Es Teh"
    assert row.unit_price == 8000


def test_database_stores_only_the_token_hash(client, menu, db):
    token = _post(client, _body(menu)).json()["data"]["tracking_token"]
    stored = db.scalars(select(Order)).one().tracking_token_hash
    assert stored != token and token not in stored
    assert stored == hashlib.sha256(token.encode()).hexdigest()


# ---- idempotency -----------------------------------------------------------------------
def test_missing_idempotency_key_is_rejected(client, menu, db):
    assert _post(client, _body(menu), key=None).status_code == 422
    assert _post(client, _body(menu), key="pendek").status_code == 422
    assert _count_orders(db) == 0


def test_same_key_returns_same_order_without_duplicating(client, menu, db):
    first = _post(client, _body(menu))
    again = _post(client, _body(menu))
    assert first.status_code == 201 and again.status_code == 200
    a, b = first.json()["data"], again.json()["data"]
    assert (a["order_id"], a["order_number"], a["tracking_token"]) == (
        b["order_id"], b["order_number"], b["tracking_token"],
    )
    assert _count_orders(db) == 1


def test_same_key_with_different_content_conflicts(client, menu, db):
    _post(client, _body(menu))
    other = _body(menu, customer_name="Orang Lain")
    r = _post(client, other)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "IDEMPOTENCY_KEY_REUSED"
    assert _count_orders(db) == 1


# ---- membaca order dengan tracking token ------------------------------------------------
def test_get_order_with_valid_token(client, menu):
    created = _post(client, _body(menu)).json()["data"]
    r = client.get(
        f"{API}/orders/{created['order_id']}",
        headers={"X-Tracking-Token": created["tracking_token"]},
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["order_number"] == "A001" and data["total"] == 45100
    assert {i["name"] for i in data["items"]} == {"Es Teh", "Nasi Goreng"}
    assert "tracking_token" not in r.text and "idempotency" not in r.text


def test_get_order_hides_existence_without_a_valid_token(client, menu):
    import uuid

    created = _post(client, _body(menu)).json()["data"]
    url = f"{API}/orders/{created['order_id']}"
    attempts = [
        client.get(url),  # tanpa token
        client.get(url, headers={"X-Tracking-Token": "token-salah"}),
        client.get(
            f"{API}/orders/{uuid.uuid4()}",
            headers={"X-Tracking-Token": created["tracking_token"]},
        ),
    ]
    for r in attempts:
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "ORDER_NOT_FOUND"
