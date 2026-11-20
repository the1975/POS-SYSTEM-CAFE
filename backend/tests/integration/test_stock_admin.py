from sqlalchemy import select

from app.modules.inventory.model import Inventory, StockMovement

API = "/api/v1"


def _stock(db, menu, name):
    return db.execute(
        select(Inventory.quantity_available).where(Inventory.product_id == menu[name])
    ).scalar_one()


def test_list_stock_admin_only_and_paginated(client, menu, staff_headers):
    assert client.get(f"{API}/inventory", headers=staff_headers("CASHIER")).status_code == 403
    r = client.get(f"{API}/inventory", headers=staff_headers("ADMIN"))
    assert r.status_code == 200
    body = r.json()
    names = {i["product_name"] for i in body["data"]}
    assert {"Es Teh", "Kopi Susu", "Nasi Goreng"} <= names
    assert "Jus 100% Jeruk" not in names  # tanpa record inventory
    assert body["pagination"]["total"] == len(body["data"])
    es = next(i for i in body["data"] if i["product_name"] == "Es Teh")
    assert es["category_name"] == "Minuman" and es["quantity_available"] == 10


def test_list_stock_search(client, menu, staff_headers):
    r = client.get(f"{API}/inventory?search=nasi", headers=staff_headers("ADMIN"))
    assert [i["product_name"] for i in r.json()["data"]] == ["Nasi Goreng"]


def test_adjust_add_reduce_and_movement_recorded(client, menu, db, staff_headers):
    h = staff_headers("ADMIN")
    url = f"{API}/inventory/{menu['es_teh']}/adjust"
    r = client.post(url, json={"quantity": 5, "reason": "Barang masuk", "movement_type": "RESTOCK"}, headers=h)
    assert r.status_code == 200 and r.json()["data"]["quantity_available"] == 15
    r = client.post(url, json={"quantity": -3, "reason": "Tumpah", "movement_type": "WASTE"}, headers=h)
    assert r.json()["data"]["quantity_available"] == 12
    assert _stock(db, menu, "es_teh") == 12
    moves = list(db.scalars(select(StockMovement).where(StockMovement.product_id == menu["es_teh"])))
    assert sorted(m.quantity for m in moves) == [-3, 5]


def test_adjust_cannot_go_negative_and_rejects_bad_input(client, menu, db, staff_headers):
    h = staff_headers("ADMIN")
    url = f"{API}/inventory/{menu['es_teh']}/adjust"
    r = client.post(url, json={"quantity": -11, "reason": "Hitung ulang", "movement_type": "ADJUSTMENT"}, headers=h)
    assert r.status_code == 409 and r.json()["error"]["code"] == "ADJUST_EXCEEDS_STOCK"
    assert _stock(db, menu, "es_teh") == 10
    bad = client.post(url, json={"quantity": 0, "reason": "Nol", "movement_type": "RESTOCK"}, headers=h)
    assert bad.status_code == 422
    wrong = client.post(url, json={"quantity": -1, "reason": "Salah tanda", "movement_type": "RESTOCK"}, headers=h)
    assert wrong.status_code == 422


def test_adjust_unknown_or_forbidden(client, menu, staff_headers):
    body = {"quantity": 1, "reason": "Coba saja", "movement_type": "RESTOCK"}
    denied = client.post(f"{API}/inventory/{menu['es_teh']}/adjust", json=body, headers=staff_headers("CASHIER"))
    assert denied.status_code == 403
    h = staff_headers("ADMIN")
    no_inv = client.post(f"{API}/inventory/{menu['jus']}/adjust", json=body, headers=h)
    assert no_inv.status_code == 404 and no_inv.json()["error"]["code"] == "PRODUCT_NOT_FOUND"


def test_set_reorder_level_shows_in_list_and_is_audited(client, menu, db, staff_headers):
    from app.modules.audit.model import AuditLog

    h = staff_headers("ADMIN")
    url = f"{API}/inventory/{menu['es_teh']}/reorder-level"
    r = client.patch(url, json={"reorder_level": 4}, headers=h)
    assert r.status_code == 200 and r.json()["data"]["reorder_level"] == 4
    rows = client.get(f"{API}/inventory?search=teh", headers=h).json()["data"]
    assert rows[0]["reorder_level"] == 4
    log = db.scalar(select(AuditLog).where(AuditLog.action == "UPDATE_REORDER_LEVEL"))
    assert log.old_value == {"reorder_level": 0} and log.new_value == {"reorder_level": 4}


def test_set_reorder_level_validation_and_access(client, menu, staff_headers):
    url = f"{API}/inventory/{menu['es_teh']}/reorder-level"
    assert client.patch(url, json={"reorder_level": 1}, headers=staff_headers("CASHIER")).status_code == 403
    h = staff_headers("ADMIN")
    assert client.patch(url, json={"reorder_level": -1}, headers=h).status_code == 422
    missing = client.patch(f"{API}/inventory/{menu['jus']}/reorder-level", json={"reorder_level": 2}, headers=h)
    assert missing.status_code == 404
