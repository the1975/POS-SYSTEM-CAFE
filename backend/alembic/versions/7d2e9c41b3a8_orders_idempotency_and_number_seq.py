"""orders: idempotency_key + sequence nomor order

Revision ID: 7d2e9c41b3a8
Revises: 4bc4401ac8fb
"""

import sqlalchemy as sa

from alembic import op

revision = "7d2e9c41b3a8"
down_revision = "4bc4401ac8fb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("idempotency_key", sa.String(length=100), nullable=True))
    op.create_unique_constraint(op.f("uq_orders_idempotency_key"), "orders", ["idempotency_key"])
    # Nomor urut order (A001, A002, ...). SEQUENCE PostgreSQL: atomik untuk request paralel.
    op.execute("CREATE SEQUENCE order_number_seq START 1")


def downgrade() -> None:
    op.execute("DROP SEQUENCE order_number_seq")
    op.drop_constraint(op.f("uq_orders_idempotency_key"), "orders", type_="unique")
    op.drop_column("orders", "idempotency_key")
