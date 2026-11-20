"""order_items: snapshot HPP (unit_cost) untuk laba kotor

Revision ID: a3c5f7d91e24
Revises: 7d2e9c41b3a8
"""

import sqlalchemy as sa

from alembic import op

revision = "a3c5f7d91e24"
down_revision = "7d2e9c41b3a8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("order_items", sa.Column("unit_cost", sa.Numeric(12, 2), nullable=True))
    # Order lama belum punya snapshot: diisi dengan HPP produk SAAT INI (perkiraan).
    op.execute(
        "UPDATE order_items SET unit_cost = "
        "(SELECT cost_price FROM products WHERE products.id = order_items.product_id)"
    )


def downgrade() -> None:
    op.drop_column("order_items", "unit_cost")
