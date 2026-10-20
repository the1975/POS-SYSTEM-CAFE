from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.modules.orders.model import Order, OrderItem
from app.modules.payments.model import Payment

API = "/api/v1/analytics"
DAY = {"start_date": "2026-10-20", "end_date": "2026-10-20"}  # satu hari penuh, zona WIB


def _order(db, lines, *, paid_at, n, status="COMPLETED", pay_status="PAID"):
    """Buat order + pembayaran langsung di DB. lines = [(product_id, qty, harga)]."""
    total = sum(Decimal(q * price) for _, q, price in lines)
    order = Order(
        order_number=f"AN-{n}",
        customer_name="Uji",
        tracking_token_hash=f"hash-analytics-{n}",
        status=status,
        subtotal=total,
        total=total,
        payment_method="CASH",
    )
    db.add(order)
    db.flush()
    for product_id, qty, price in lines:
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product_id,
                product_name_snapshot="x",
                unit_price=Decimal(price),
                quantity=qty,
                subtotal=Decimal(qty * price),
            )
        )
    db.add(
        Payment(
            order_id=order.id,
            provider="CASH",
            payment_method="CASH",
            amount=total,
            status=pay_status,
            paid_at=paid_at,
        )
    )
    db.commit()


@pytest.fixture
def sales(db, menu):
    """Penjualan uji. Waktu disimpan UTC; WIB = UTC+7."""
    es, nasi = menu["es_teh"], menu["nasi"]
    utc = lambda d, h, m=0: datetime(2026, 10, d, h, m, tzinfo=UTC)  # noqa: E731
    # Masuk 20 Okt WIB:
    _order(db, [(es, 2, 8000), (nasi, 1, 25000)], paid_at=utc(20, 3), n=1)  # 10.00 WIB, 41000
    _order(db, [(nasi, 2, 25000)], paid_at=utc(20, 5, 30), n=2)  # 12.30 WIB, 50000
    _order(db, [(es, 1, 8000)], paid_at=utc(19, 17, 30), n=3)  # 00.30 WIB 20 Okt, 8000
    # Di luar / tidak dihitung:
    _order(db, [(es, 5, 8000)], paid_at=utc(20, 17, 30), n=4)  # 00.30 WIB 21 Okt
    _order(db, [(es, 1, 8000)], paid_at=None, n=5, status="PENDING", pay_status="PENDING")
    _order(db, [(es, 3, 8000)], paid_at=utc(20, 4), n=6, pay_status="REFUNDED")
    _order(db, [(es, 4, 8000)], paid_at=utc(20, 4), n=7, status="CANCELLED")


@pytest.mark.parametrize("path", ["/summary", "/products/top", "/peak-hours"])
def test_only_admin_can_see_analytics(client, staff_headers, path):
    assert client.get(f"{API}{path}").status_code == 401
    for role in ("CASHIER", "CONTROLLER"):
        assert client.get(f"{API}{path}", headers=staff_headers(role)).status_code == 403


def test_summary_counts_only_paid_orders_in_wib_day(client, staff_headers, sales):
    admin = staff_headers("ADMIN")
    r = client.get(f"{API}/summary", params=DAY, headers=admin)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["revenue"] == 99000  # 41000 + 50000 + 8000
    assert data["orders"] == 3
    assert data["units_sold"] == 6
    assert data["average_order_value"] == 33000
    assert data["start_date"] == "2026-10-20"
    # Tidak ikut: belum lunas, di-refund, dibatalkan, dan order 21 Okt WIB.


def test_summary_range_covers_next_day(client, staff_headers, sales):
    admin = staff_headers("ADMIN")
    r = client.get(
        f"{API}/summary",
        params={"start_date": "2026-10-20", "end_date": "2026-10-21"},
        headers=admin,
    )
    assert r.json()["data"]["orders"] == 4  # order 4 (00.30 WIB 21 Okt) ikut


def test_summary_empty_is_zero_not_error(client, staff_headers):
    admin = staff_headers("ADMIN")
    r = client.get(f"{API}/summary", headers=admin)  # default: hari ini, belum ada order
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["orders"] == 0
    assert data["revenue"] == 0
    assert data["average_order_value"] == 0
    assert data["start_date"] == data["end_date"]


def test_top_products_ordered_and_limited(client, staff_headers, sales, menu):
    admin = staff_headers("ADMIN")
    r = client.get(f"{API}/products/top", params=DAY, headers=admin)
    assert r.status_code == 200
    rows = r.json()["data"]
    # Es Teh dan Nasi Goreng sama-sama 3 unit; omzet lebih besar menang.
    assert [x["product_name"] for x in rows] == ["Nasi Goreng", "Es Teh"]
    assert rows[0]["units_sold"] == 3
    assert rows[0]["revenue"] == 75000
    assert rows[1]["revenue"] == 24000
    assert rows[0]["product_id"] == str(menu["nasi"])
    r = client.get(f"{API}/products/top", params={**DAY, "limit": 1}, headers=admin)
    assert len(r.json()["data"]) == 1


def test_peak_hours_has_24_hours_in_wib(client, staff_headers, sales):
    admin = staff_headers("ADMIN")
    r = client.get(f"{API}/peak-hours", params=DAY, headers=admin)
    assert r.status_code == 200
    rows = r.json()["data"]
    assert [x["hour"] for x in rows] == list(range(24))
    by_hour = {x["hour"]: x["orders"] for x in rows}
    assert by_hour[0] == 1  # 00.30 WIB
    assert by_hour[10] == 1  # 03.00 UTC
    assert by_hour[12] == 1  # 05.30 UTC
    assert sum(by_hour.values()) == 3


def test_invalid_ranges_and_params_rejected(client, staff_headers):
    admin = staff_headers("ADMIN")
    reversed_range = {"start_date": "2026-10-21", "end_date": "2026-10-20"}
    r = client.get(f"{API}/summary", params=reversed_range, headers=admin)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_DATE_RANGE"
    too_long = {"start_date": "2025-01-01", "end_date": "2026-10-20"}
    r = client.get(f"{API}/summary", params=too_long, headers=admin)
    assert r.status_code == 422  # lebih dari 366 hari
    bad = client.get(f"{API}/summary", params={"start_date": "bukan-tanggal"}, headers=admin)
    assert bad.status_code == 422
    for limit in (0, 21):
        r = client.get(f"{API}/products/top", params={"limit": limit}, headers=admin)
        assert r.status_code == 422
