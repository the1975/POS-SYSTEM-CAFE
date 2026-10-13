from app.db import models  # noqa: F401
from app.db.base import Base
from app.modules.orders.model import OrderItemStatus, OrderStatus, PaymentMethod

T = Base.metadata.tables


def _names(table) -> str:
    return " ".join(str(c.name) for c in table.constraints if c.name)


def test_all_tables_registered():
    expected = {
        "roles",
        "users",
        "categories",
        "products",
        "inventory",
        "stock_movements",
        "stock_reservations",
        "orders",
        "order_items",
        "order_revisions",
        "order_revision_items",
    }
    assert expected <= set(T)


def test_order_identity_and_guest_token():
    t = T["orders"]
    assert t.c.order_number.unique and not t.c.order_number.nullable
    assert t.c.tracking_token_hash.unique and not t.c.tracking_token_hash.nullable
    # order_number BUKAN primary key; PK adalah UUID internal.
    assert [c.name for c in t.primary_key.columns] == ["id"]
    assert not hasattr(t.c, "queue_position")


def test_order_status_values_match_spec():
    assert {s.value for s in OrderStatus} == {
        "PENDING",
        "CONFIRMED",
        "PREPARING",
        "READY",
        "COMPLETED",
        "CANCELLED",
        "OVERDUE",
    }
    assert "DELIVERING" not in {s.value for s in OrderStatus}
    assert {p.value for p in PaymentMethod} == {"QRIS", "CASH"}
    assert {i.value for i in OrderItemStatus} == {"PENDING", "PREPARING", "READY", "REMAKE"}


def test_order_money_checks():
    names = _names(T["orders"])
    for needed in (
        "subtotal_non_negative",
        "discount_non_negative",
        "tax_non_negative",
        "total_non_negative",
        "discount_within_subtotal",
        "status_valid",
        "payment_method_valid",
    ):
        assert needed in names


def test_order_indexes():
    cols = {c.name for i in T["orders"].indexes for c in i.columns}
    assert {"status", "created_at"} <= cols


def test_order_items_snapshot_columns_required():
    t = T["order_items"]
    for col in ("product_name_snapshot", "unit_price", "quantity", "subtotal"):
        assert not t.c[col].nullable
    assert "quantity_positive" in _names(t)
    assert {fk.target_fullname for fk in t.c.order_id.foreign_keys} == {"orders.id"}


def test_revision_unique_per_order():
    t = T["order_revisions"]
    uniques = [
        {c.name for c in c_.columns}
        for c_ in t.constraints
        if c_.__class__.__name__ == "UniqueConstraint"
    ]
    assert {"order_id", "revision_number"} in uniques
    assert t.c.created_by.nullable


def test_revision_items_snapshot():
    t = T["order_revision_items"]
    assert not t.c.product_name_snapshot.nullable and not t.c.unit_price.nullable
    assert {fk.target_fullname for fk in t.c.order_revision_id.foreign_keys} == {
        "order_revisions.id"
    }


def test_stock_reservation_rules():
    t = T["stock_reservations"]
    assert "quantity_positive" in _names(t) and "status_valid" in _names(t)
    assert {fk.target_fullname for fk in t.c.order_id.foreign_keys} == {"orders.id"}
    assert t.c.released_at.nullable and not t.c.expires_at.nullable
    assert "ix_stock_reservations_status_expires" in {i.name for i in t.indexes}


def test_product_availability_index():
    assert "ix_products_is_available" in {i.name for i in T["products"].indexes}
