"""v0.0.12: allow advances to compensate existing receivables.

Revision ID: e41a7c62b5f0
Revises: d93f20b51c44
"""
from alembic import op
import sqlalchemy as sa

revision = "e41a7c62b5f0"
down_revision = "d93f20b51c44"
branch_labels = None
depends_on = None


def upgrade():
    # Existing rows were created while a closing was being calculated, so
    # they are closing deductions and are already reflected in net_amount.
    with op.batch_alter_table("advance_deductions") as batch:
        batch.drop_constraint("uq_advance_payment_deduction", type_="unique")
        batch.add_column(sa.Column("kind", sa.String(length=20), nullable=False, server_default="closing"))
        batch.create_index("ix_advance_deductions_kind", ["kind"], unique=False)
        batch.create_unique_constraint("uq_advance_payment_kind_deduction", ["advance_id", "payment_id", "kind"])


def downgrade():
    with op.batch_alter_table("advance_deductions") as batch:
        batch.drop_constraint("uq_advance_payment_kind_deduction", type_="unique")
        batch.drop_index("ix_advance_deductions_kind")
        batch.drop_column("kind")
        batch.create_unique_constraint("uq_advance_payment_deduction", ["advance_id", "payment_id"])
