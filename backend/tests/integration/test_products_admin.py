import uuid

from sqlalchemy import select

from app.modules.audit.model import AuditLog

API = "/api/v1"


def _body(menu, **override):
    body = {
        "category_id": str(menu["drinks"]),
        "name": "  Teh Tarik ",
        "description": "Teh susu",
        "price": 12000,
        "cost_price": 5000,
    }
    body.update(override)
    return body


def _audits(db, product_id):
    return list(db.scalars(select(AuditLog).where(AuditLog.entity_id == product_id)))


def test_only_admin_can_create_or_update(client, menu, staff_headers):
    cashier = staff_headers("CASHIER")
    pid = menu["es_teh"]
    assert client.post(f"{API}/products", json=_body(menu), headers=cashier).status_code == 403
    r = client.patch(f"{API}/products/{pid}", json={"name": "X"}, headers=cashier)
    assert r.status_code == 403
    assert client.post(f"{API}/products", json=_body(menu)).status_code == 401
    assert client.patch(f"{API}/products/{pid}", json={"name": "X"}).status_code == 401


def test_admin_creates_product_with_audit(client, db, menu, staff_headers):
    admin = staff_headers("ADMIN")
    r = client.post(f"{API}/products", json=_body(menu), headers=admin)
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["name"] == "Teh Tarik"  # spasi pinggir dibuang
    assert data["price"] == 12000
    assert data["cost_price"] == 5000  # admin boleh lihat HPP
    assert data["is_available"] is True
    logs = _audits(db, uuid.UUID(data["id"]))
    assert [log.action for log in logs] == ["CREATE_PRODUCT"]
    # Produk baru langsung tampil di menu customer (belum ada stok -> in_stock false).
    pub = client.get(f"{API}/products/{data['id']}")
    assert pub.status_code == 200
    assert pub.json()["data"]["in_stock"] is False
    assert "cost_price" not in pub.text


def test_create_rejects_bad_input(client, menu, staff_headers):
    admin = staff_headers("ADMIN")
    for override in (
        {"price": -1},
        {"cost_price": -5},
        {"name": "   "},
        {"price": "abc"},
    ):
        r = client.post(f"{API}/products", json=_body(menu, **override), headers=admin)
        assert r.status_code == 422, override
    unknown = "00000000-0000-0000-0000-000000000001"
    r = client.post(f"{API}/products", json=_body(menu, category_id=unknown), headers=admin)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_CATEGORY"


def test_price_change_is_audited_with_old_and_new(client, db, menu, staff_headers):
    admin = staff_headers("ADMIN")
    pid = menu["es_teh"]
    r = client.patch(f"{API}/products/{pid}", json={"price": 9000}, headers=admin)
    assert r.status_code == 200
    assert r.json()["data"]["price"] == 9000
    log = _audits(db, pid)[0]
    assert log.action == "UPDATE_PRODUCT_PRICE"
    assert log.old_value == {"price": 8000}
    assert log.new_value == {"price": 9000}


def test_hide_and_show_product_instead_of_delete(client, menu, staff_headers):
    admin = staff_headers("ADMIN")
    pid = menu["es_teh"]
    r = client.patch(f"{API}/products/{pid}", json={"is_available": False}, headers=admin)
    assert r.status_code == 200
    assert client.get(f"{API}/products/{pid}").status_code == 404  # hilang dari menu
    r = client.patch(f"{API}/products/{pid}", json={"is_available": True}, headers=admin)
    assert r.status_code == 200
    assert client.get(f"{API}/products/{pid}").status_code == 200  # muncul lagi
    # Tidak ada hapus fisik.
    assert client.delete(f"{API}/products/{pid}", headers=admin).status_code == 405


def test_patch_edge_cases(client, db, menu, staff_headers):
    admin = staff_headers("ADMIN")
    pid = menu["es_teh"]
    # body kosong / field wajib null ditolak
    assert client.patch(f"{API}/products/{pid}", json={}, headers=admin).status_code == 422
    r = client.patch(f"{API}/products/{pid}", json={"name": None}, headers=admin)
    assert r.status_code == 422
    # produk tidak ada
    r = client.patch(
        f"{API}/products/00000000-0000-0000-0000-000000000001",
        json={"name": "X"},
        headers=admin,
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "PRODUCT_NOT_FOUND"
    # tidak ada yang berubah -> 200 tanpa audit
    r = client.patch(f"{API}/products/{pid}", json={"name": "Es Teh"}, headers=admin)
    assert r.status_code == 200
    assert _audits(db, pid) == []
    # deskripsi bisa dikosongkan dengan null
    client.patch(f"{API}/products/{pid}", json={"description": "Segar"}, headers=admin)
    r = client.patch(f"{API}/products/{pid}", json={"description": None}, headers=admin)
    assert r.json()["data"]["description"] is None


def test_admin_list_requires_admin(client, staff_headers):
    cashier = staff_headers("CASHIER")
    assert client.get(f"{API}/admin/products", headers=cashier).status_code == 403
    assert client.get(f"{API}/admin/products").status_code == 401


def test_admin_list_shows_all_products_with_cost_and_category(client, menu, staff_headers):
    admin = staff_headers("ADMIN")
    r = client.get(f"{API}/admin/products", headers=admin)
    assert r.status_code == 200
    body = r.json()
    assert body["pagination"]["total"] == 6  # termasuk yang disembunyikan & kategori nonaktif
    by_name = {p["name"]: p for p in body["data"]}
    assert by_name["Mie Goreng"]["is_available"] is False
    assert by_name["Es Teh"]["cost_price"] == 1000
    assert by_name["Es Teh"]["category_name"] == "Minuman"
    assert by_name["Menu Rahasia"]["category_name"] == "Rahasia"


def test_admin_list_filters(client, menu, staff_headers):
    admin = staff_headers("ADMIN")

    def names(query):
        r = client.get(f"{API}/admin/products?{query}", headers=admin)
        assert r.status_code == 200
        return {p["name"] for p in r.json()["data"]}

    assert names("is_available=false") == {"Mie Goreng"}
    assert names("search=nasi") == {"Nasi Goreng"}
    assert names("search=100%25") == {"Jus 100% Jeruk"}  # % dianggap teks biasa
    assert names(f"category_id={menu['drinks']}") == {"Es Teh", "Kopi Susu"}
