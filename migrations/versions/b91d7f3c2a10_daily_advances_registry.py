"""Daily works, advances, payment totals and unique holes.

Revision ID: b91d7f3c2a10
Revises: 44789ee52718
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

revision = "b91d7f3c2a10"
down_revision = "44789ee52718"
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    duplicates = conn.execute(sa.text("SELECT quantity, COUNT(*) c FROM holes GROUP BY quantity HAVING COUNT(*) > 1")).fetchall()
    if duplicates:
        values = ", ".join(str(row[0]) for row in duplicates)
        raise RuntimeError(f"Não é possível aplicar UNIQUE em holes.quantity; duplicatas: {values}")
    with op.batch_alter_table("holes") as batch:
        batch.create_unique_constraint("uq_holes_quantity", ["quantity"])
    with op.batch_alter_table("payments") as batch:
        batch.add_column(sa.Column("gross_amount", sa.Numeric(12,2), nullable=False, server_default="0"))
        batch.add_column(sa.Column("advance_amount", sa.Numeric(12,2), nullable=False, server_default="0"))
        batch.add_column(sa.Column("net_amount", sa.Numeric(12,2), nullable=False, server_default="0"))
    conn.execute(sa.text("UPDATE payments SET gross_amount=total_amount, net_amount=total_amount, advance_amount=0"))
    op.create_table("advances",
        sa.Column("id",sa.Integer(),primary_key=True), sa.Column("date",sa.Date(),nullable=False),
        sa.Column("amount",sa.Numeric(12,2),nullable=False), sa.Column("observation",sa.Text()),
        sa.Column("created_at",sa.DateTime(),nullable=False))
    op.create_index("ix_advances_date","advances",["date"])
    op.create_table("daily_works",
        sa.Column("id",sa.Integer(),primary_key=True), sa.Column("date",sa.Date(),nullable=False),
        sa.Column("fraction",sa.Numeric(2,1),nullable=False), sa.Column("daily_rate",sa.Numeric(12,2),nullable=False),
        sa.Column("total_amount",sa.Numeric(12,2),nullable=False), sa.Column("description",sa.String(150),nullable=False),
        sa.Column("observation",sa.Text()), sa.Column("created_at",sa.DateTime(),nullable=False),
        sa.Column("payment_id",sa.Integer(),sa.ForeignKey("payments.id")),
        sa.CheckConstraint("fraction IN (0.5, 1.0)",name="ck_daily_work_fraction"))
    op.create_index("ix_daily_works_date","daily_works",["date"]); op.create_index("ix_daily_works_payment_id","daily_works",["payment_id"])
    op.create_table("advance_deductions",
        sa.Column("id",sa.Integer(),primary_key=True), sa.Column("advance_id",sa.Integer(),sa.ForeignKey("advances.id"),nullable=False),
        sa.Column("payment_id",sa.Integer(),sa.ForeignKey("payments.id"),nullable=False), sa.Column("amount",sa.Numeric(12,2),nullable=False),
        sa.UniqueConstraint("advance_id","payment_id",name="uq_advance_payment_deduction"))
    op.create_index("ix_advance_deductions_advance_id","advance_deductions",["advance_id"]); op.create_index("ix_advance_deductions_payment_id","advance_deductions",["payment_id"])

def downgrade():
    op.drop_table("advance_deductions"); op.drop_table("daily_works"); op.drop_table("advances")
    with op.batch_alter_table("payments") as batch:
        batch.drop_column("net_amount"); batch.drop_column("advance_amount"); batch.drop_column("gross_amount")
    with op.batch_alter_table("holes") as batch: batch.drop_constraint("uq_holes_quantity",type_="unique")
