import uuid
from decimal import Decimal

import pytest

from app.core.security import derive_tracking_token, hash_token, verify_token
from app.modules.orders.order_number import format_order_number
from app.modules.orders.pricing import calculate_totals


def test_order_number_format_and_rollover():
    assert [format_order_number(n) for n in (1, 127, 999, 1000, 1999)] == [
        "A001",
        "A127",
        "A999",
        "B001",
        "C001",
    ]
    assert format_order_number(26 * 999) == "Z999"
    assert format_order_number(26 * 999 + 1) == "AA001"  # setelah Z lanjut ke dua huruf


def test_order_number_rejects_invalid_sequence():
    with pytest.raises(ValueError):
        format_order_number(0)


def test_order_numbers_are_unique_over_a_long_range():
    numbers = {format_order_number(n) for n in range(1, 60_000)}
    assert len(numbers) == 59_999


def test_totals_match_spec_example():
    # Contoh dari dokumen: subtotal 100.000, diskon 10.000, DPP 90.000, pajak 9.000, total 99.000.
    t = calculate_totals(Decimal(100000), Decimal(10000), Decimal(10))
    assert (t.taxable_base, t.tax_amount, t.total) == (
        Decimal(90000),
        Decimal(9000),
        Decimal(99000),
    )


def test_tax_rounds_half_up_to_whole_rupiah():
    assert calculate_totals(Decimal(1005), Decimal(0), Decimal(10)).tax_amount == Decimal(101)


def test_discount_cannot_exceed_subtotal_or_be_negative():
    with pytest.raises(ValueError):
        calculate_totals(Decimal(100), Decimal(101), Decimal(10))
    with pytest.raises(ValueError):
        calculate_totals(Decimal(100), Decimal(-1), Decimal(10))


def test_total_is_zero_not_negative_when_fully_discounted():
    t = calculate_totals(Decimal(100), Decimal(100), Decimal(10))
    assert t.total == Decimal(0)


def test_tracking_token_is_deterministic_per_order_and_unique_across_orders():
    a, b = uuid.uuid4(), uuid.uuid4()
    assert derive_tracking_token(a) == derive_tracking_token(a)
    assert derive_tracking_token(a) != derive_tracking_token(b)
    assert len(derive_tracking_token(a)) >= 43  # 256-bit


def test_token_hash_verification():
    token = derive_tracking_token(uuid.uuid4())
    stored = hash_token(token)
    assert stored != token
    assert verify_token(token, stored)
    assert not verify_token(token + "x", stored)
    assert not verify_token("", stored)
