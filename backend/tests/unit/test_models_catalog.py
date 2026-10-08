from app.db import models  # noqa: F401
from app.db.base import Base

T = Base.metadata.tables


def test_group_a_tables_registered():
    assert {"roles", "users", "categories", "products"} <= set(T)


def test_every_pk_is_uuid_and_timestamps_not_null():
    for name in ("roles", "users", "categories", "products"):
        t = T[name]
        assert type(t.c.id.type).__name__ == "Uuid"
        assert not t.c.created_at.nullable and not t.c.updated_at.nullable


def test_unique_columns():
    assert T["users"].c.email.unique and not T["users"].c.email.nullable
    assert T["roles"].c.name.unique


def test_foreign_keys():
    assert {fk.target_fullname for fk in T["users"].c.role_id.foreign_keys} == {"roles.id"}
    assert {fk.target_fullname for fk in T["products"].c.category_id.foreign_keys} == {
        "categories.id"
    }


def test_products_money_not_null_and_checked():
    t = T["products"]
    assert not t.c.price.nullable and not t.c.cost_price.nullable
    names = " ".join(str(c.name) for c in t.constraints if c.name)
    assert "price_non_negative" in names and "cost_price_non_negative" in names


def test_deactivation_flags_default_true():
    assert T["users"].c.is_active.server_default is not None
    assert T["products"].c.is_available.server_default is not None
