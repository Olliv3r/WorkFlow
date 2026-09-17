"""Receipts and allocations for partial/accrued payments.

Revision ID: c82e91a740b3
Revises: b91d7f3c2a10
"""
from alembic import op
import sqlalchemy as sa

revision = "c82e91a740b3"
down_revision = "b91d7f3c2a10"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "receipts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("observation", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_receipts_date", "receipts", ["date"])
    op.create_table(
        "receipt_allocations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("receipt_id", sa.Integer(), sa.ForeignKey("receipts.id"), nullable=False),
        sa.Column("payment_id", sa.Integer(), sa.ForeignKey("payments.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.UniqueConstraint("receipt_id", "payment_id", name="uq_receipt_payment_allocation"),
    )
    op.create_index("ix_receipt_allocations_receipt_id", "receipt_allocations", ["receipt_id"])
    op.create_index("ix_receipt_allocations_payment_id", "receipt_allocations", ["payment_id"])

    # Compatibilidade histórica: pagamentos que a versão anterior marcou como
    # paid representam recebimentos integrais conhecidos. Materializamos isso
    # como Receipt + Allocation sem alterar o valor histórico do fechamento.
    conn = op.get_bind()
    rows = conn.execute(sa.text(
        "SELECT id, COALESCE(payment_date, end_period) AS received_date, net_amount "
        "FROM payments WHERE status='paid' AND net_amount > 0"
    )).fetchall()
    for row in rows:
        result = conn.execute(sa.text(
            "INSERT INTO receipts (date, amount, observation, created_at) "
            "VALUES (:date, :amount, :obs, CURRENT_TIMESTAMP)"
        ), {"date": row.received_date, "amount": row.net_amount,
            "obs": "Migrado automaticamente de pagamento marcado como pago."})
        receipt_id = result.lastrowid
        if receipt_id is None:
            receipt_id = conn.execute(sa.text("SELECT MAX(id) FROM receipts")).scalar()
        conn.execute(sa.text(
            "INSERT INTO receipt_allocations (receipt_id, payment_id, amount) "
            "VALUES (:receipt_id, :payment_id, :amount)"
        ), {"receipt_id": receipt_id, "payment_id": row.id, "amount": row.net_amount})


def downgrade():
    op.drop_table("receipt_allocations")
    op.drop_table("receipts")
