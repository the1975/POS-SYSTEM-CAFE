import pytest

API = "/api/v1"


def _place_order(client, menu, key, method="CASH", name="Leo"):
    body = {
        "customer_name": name,
        "items": [{"product_id": str(menu["es_teh"]), "quantity": 1}],
        "payment_method": method,
    }
    r = client.post(f"{API}/orders", json=body, headers={"Idempotency-Key": key})
    assert r.status_code == 201
    return r.json()["data"]


def _list(client, headers, **params):
    return client.get(f"{API}/staff/orders", params=params, headers=headers)


def test_cashier_finds_waiting_cash_order_and_confirms_it(client, menu, staff_headers):
    headers = staff_headers("CASHIER", "kasir@example.com")
    cash_order = _place_order(client, menu, "kunci-staff-001", "CASH", "Budi")
    _place_order(client, menu, "kunci-staff-002", "QRIS", "Sari")

    r = _list(client, headers, payment_status="WAITING_CASH")
    assert r.status_code == 200
    body = r.json()
    assert body["pagination"]["total"] == 1
    item = body["data"][0]
    assert item["order_number"] == cash_order["order_number"]
    assert item["status"] == "PENDING"
    assert (item["payment_method"], item["payment_status"]) == ("CASH", "WAITING_CASH")
    assert "tracking_token" not in r.text

    # payment_id dari daftar ini langsung bisa dipakai kasir untuk konfirmasi.
    confirm = client.post(
        f"{API}/payments/{item['payment_id']}/cash-confirm",
        json={"cash_received": item["total"]},
        headers=headers,
    )
    assert confirm.status_code == 200
    assert _list(client, headers, payment_status="WAITING_CASH").json()["pagination"]["total"] == 0


def test_filter_by_order_status(client, menu, staff_headers):
    headers = staff_headers("CASHIER", "kasir@example.com")
    _place_order(client, menu, "kunci-staff-003")
    _place_order(client, menu, "kunci-staff-004")
    assert _list(client, headers, status="PENDING").json()["pagination"]["total"] == 2
    assert _list(client, headers, status="CONFIRMED").json()["pagination"]["total"] == 0


def test_search_by_name_and_order_number(client, menu, staff_headers):
    headers = staff_headers("CASHIER", "kasir@example.com")
    first = _place_order(client, menu, "kunci-staff-005", name="Budi")
    _place_order(client, menu, "kunci-staff-006", name="Sari")

    by_name = _list(client, headers, search="bud").json()
    assert [o["customer_name"] for o in by_name["data"]] == ["Budi"]
    by_number = _list(client, headers, search=first["order_number"]).json()
    assert by_number["pagination"]["total"] == 1
    # % dianggap teks biasa, bukan wildcard.
    assert _list(client, headers, search="%").json()["pagination"]["total"] == 0


def test_pagination(client, menu, staff_headers):
    headers = staff_headers("CASHIER", "kasir@example.com")
    for i in range(3):
        _place_order(client, menu, f"kunci-staff-10{i}")
    page1 = _list(client, headers, page=1, page_size=2).json()
    assert len(page1["data"]) == 2
    assert (page1["pagination"]["total"], page1["pagination"]["total_pages"]) == (3, 2)
    assert len(_list(client, headers, page=2, page_size=2).json()["data"]) == 1


def test_staff_orders_requires_login(client):
    assert client.get(f"{API}/staff/orders").status_code == 401


@pytest.mark.parametrize("role", ["CASHIER", "KITCHEN", "CONTROLLER", "PICKUP", "ADMIN"])
def test_every_staff_role_can_list_orders(client, staff_headers, role):
    assert _list(client, staff_headers(role)).status_code == 200


def test_invalid_filter_value_is_rejected(client, staff_headers):
    r = _list(client, staff_headers("CASHIER"), status="NGAWUR")
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"
