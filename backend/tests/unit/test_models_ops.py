from app.db import models  # noqa: F401
from app.db.base import Base
from app.modules.kitchen.model import RemakeReason
from app.modules.payments.model import PaymentStatus

T = Base.metadata.tables

ALL_18 = {
    "roles", "users", "categories", "products", "inventory", "stock_reservations",
    "stock_movements", "orders", "order_items", "order_revisions", "order_revision_items",
    "payments", "payment_events", "order_status_history", "remake_events", "pickups",
    "notifications", "audit_logs",
}


def _names(table) -> str:
    return " ".join(str(c.name) for c in table.constraints if c.name)


def _fk(col) -> set[str]:
    return {fk.target_fullname for fk in col.foreign_keys}


def test_all_18_entities_exist():
    assert set(T) == ALL_18


def test_payment_status_values_match_spec():
    assert {s.value for s in PaymentStatus} == {
        "PENDING", "WAITING_CASH", "PAID", "FAILED",
        "REFUND_REQUESTED", "REFUND_PENDING", "REFUNDED", "REFUND_FAILED",
    }


def test_payment_idempotency_keys():
    p = T["payments"]
    assert p.c.provider_transaction_id.unique and p.c.provider_transaction_id.nullable
    assert "amount_positive" in _names(p)
    assert _fk(p.c.order_id) == {"orders.id"}
    e = T["payment_events"]
    assert e.c.event_id.unique and not e.c.event_id.nullable
    assert type(e.c.payload.type).__name__ == "JSONB" and not e.c.payload.nullable


def test_status_history_links_and_nullable_actor():
    t = T["order_status_history"]
    assert t.c.from_status.nullable and not t.c.to_status.nullable
    assert t.c.changed_by.nullable
    assert "to_status_valid" in _names(t) and "from_status_valid" in _names(t)


def test_remake_uses_same_order_item():
    t = T["remake_events"]
    assert _fk(t.c.order_item_id) == {"order_items.id"}
    assert not hasattr(t.c, "order_id")
    assert {r.value for r in RemakeReason} == {
        "WRONG_MENU", "WRONG_SIZE", "WRONG_TOPPING", "WRONG_QUANTITY",
        "DAMAGED_OR_SPILLED", "CUSTOMER_REQUEST", "OTHER",
    }
    assert not t.c.created_by.nullable


def test_pickup_one_per_order_and_hashed_token():
    t = T["pickups"]
    assert t.c.order_id.unique and t.c.pickup_token_hash.unique
    assert not t.c.pickup_token_hash.nullable
    assert "completed_has_timestamp" in _names(t)
    assert t.c.verified_by.nullable


def test_notification_guest_has_no_user_fk():
    t = T["notifications"]
    assert t.c.recipient_id.nullable and not t.c.recipient_id.foreign_keys
    assert _fk(t.c.order_id) == {"orders.id"}


def test_audit_log_indexes_and_json():
    t = T["audit_logs"]
    indexed = {c.name for i in t.indexes for c in i.columns}
    assert {"user_id", "entity_type", "entity_id", "created_at"} <= indexed
    assert type(t.c.old_value.type).__name__ == "JSONB" and t.c.old_value.nullable


def test_no_cascade_delete_on_transaction_history():
    # Riwayat transaksi tidak boleh ikut terhapus: semua FK memakai RESTRICT.
    for t in T.values():
        for fk in t.foreign_keys:
            assert fk.ondelete == "RESTRICT", f"{t.name}.{fk.parent.name}"


def test_cash_columns_optional_and_checked():
    t = T["payments"]
    assert t.c.cash_received.nullable and t.c.change_amount.nullable
    names = _names(t)
    assert "cash_received_covers_amount" in names and "change_non_negative" in names
