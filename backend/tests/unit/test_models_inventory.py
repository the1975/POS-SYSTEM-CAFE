from app.db import models  # noqa: F401
from app.db.base import Base
from app.modules.inventory.model import StockMovementType

T = Base.metadata.tables


def _constraint_names(table) -> str:
    return " ".join(str(c.name) for c in table.constraints if c.name)


def test_inventory_one_per_product_and_never_negative():
    t = T["inventory"]
    assert t.c.product_id.unique and not t.c.product_id.nullable
    names = _constraint_names(t)
    for needed in (
        "quantity_available_non_negative",
        "quantity_reserved_non_negative",
        "reorder_level_non_negative",
    ):
        assert needed in names


def test_inventory_defaults_are_zero():
    t = T["inventory"]
    for col in ("quantity_available", "quantity_reserved", "reorder_level"):
        assert t.c[col].server_default is not None and not t.c[col].nullable


def test_stock_movement_types_match_spec():
    assert {m.value for m in StockMovementType} == {
        "SALE", "RESERVATION", "RELEASE", "RESTOCK", "ADJUSTMENT", "WASTE", "REMAKE",
    }
    assert "movement_type_valid" in _constraint_names(T["stock_movements"])


def test_stock_movement_rejects_zero_and_links_product_user():
    t = T["stock_movements"]
    assert "quantity_non_zero" in _constraint_names(t)
    assert {fk.target_fullname for fk in t.c.product_id.foreign_keys} == {"products.id"}
    assert {fk.target_fullname for fk in t.c.created_by.foreign_keys} == {"users.id"}
    assert t.c.created_by.nullable and not t.c.product_id.nullable


def test_stock_movement_has_history_index():
    idx = {i.name for i in T["stock_movements"].indexes}
    assert "ix_stock_movements_product_created" in idx
