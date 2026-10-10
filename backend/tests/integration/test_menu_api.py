import uuid

API = "/api/v1"


def _names(resp) -> list[str]:
    return [p["name"] for p in resp.json()["data"]]


def test_categories_only_active_in_order(client, menu):
    r = client.get(f"{API}/categories")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert [c["name"] for c in body["data"]] == ["Minuman", "Makanan"]


def test_category_detail_and_hidden_category_is_404(client, menu):
    assert client.get(f"{API}/categories/{menu['drinks']}").status_code == 200
    r = client.get(f"{API}/categories/{menu['secret']}")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "CATEGORY_NOT_FOUND"


def test_products_hide_unavailable_and_inactive_category(client, menu):
    names = _names(client.get(f"{API}/products"))
    assert "Mie Goreng" not in names  # is_available = false
    assert "Menu Rahasia" not in names  # kategori nonaktif
    assert set(names) == {"Es Teh", "Kopi Susu", "Nasi Goreng", "Jus 100% Jeruk"}


def test_products_never_expose_cost_price(client, menu):
    r = client.get(f"{API}/products")
    assert "cost_price" not in r.text


def test_default_order_is_category_then_name(client, menu):
    assert _names(client.get(f"{API}/products")) == [
        "Es Teh", "Kopi Susu", "Jus 100% Jeruk", "Nasi Goreng",
    ]


def test_in_stock_flag(client, menu):
    data = {p["name"]: p for p in client.get(f"{API}/products").json()["data"]}
    assert data["Es Teh"]["in_stock"] is True
    assert data["Kopi Susu"]["in_stock"] is False  # stok 0
    assert data["Jus 100% Jeruk"]["in_stock"] is False  # tidak ada record inventory


def test_price_is_a_json_number(client, menu):
    data = {p["name"]: p for p in client.get(f"{API}/products").json()["data"]}
    assert data["Nasi Goreng"]["price"] == 25000
    assert isinstance(data["Nasi Goreng"]["price"], int)


def test_filter_by_category(client, menu):
    r = client.get(f"{API}/products", params={"category_id": str(menu["food"])})
    assert _names(r) == ["Jus 100% Jeruk", "Nasi Goreng"]


def test_search_is_case_insensitive(client, menu):
    assert _names(client.get(f"{API}/products", params={"search": "NASI"})) == ["Nasi Goreng"]


def test_search_treats_percent_as_plain_text(client, menu):
    # Tanpa autoescape, "%" akan cocok dengan SEMUA produk.
    assert _names(client.get(f"{API}/products", params={"search": "%"})) == ["Jus 100% Jeruk"]


def test_sort_by_price(client, menu):
    asc = _names(client.get(f"{API}/products", params={"sort": "price"}))
    desc = _names(client.get(f"{API}/products", params={"sort": "-price"}))
    assert asc == ["Es Teh", "Jus 100% Jeruk", "Kopi Susu", "Nasi Goreng"]
    assert desc == list(reversed(asc))


def test_pagination(client, menu):
    r = client.get(f"{API}/products", params={"page": 2, "page_size": 3})
    body = r.json()
    assert body["pagination"] == {"page": 2, "page_size": 3, "total": 4, "total_pages": 2}
    assert len(body["data"]) == 1


def test_page_size_limit_is_validated(client, menu):
    r = client.get(f"{API}/products", params={"page_size": 101})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"


def test_product_detail(client, menu):
    r = client.get(f"{API}/products/{menu['es_teh']}")
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "Es Teh"
    assert "cost_price" not in r.text


def test_hidden_or_unknown_product_is_404(client, menu):
    for pid in (menu["mie"], menu["rahasia"], uuid.uuid4()):
        r = client.get(f"{API}/products/{pid}")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "PRODUCT_NOT_FOUND"


def test_malformed_uuid_is_422(client, menu):
    assert client.get(f"{API}/products/bukan-uuid").status_code == 422
