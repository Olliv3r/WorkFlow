"""Work rules v0.0.11: manual daily values, nullable holes and catalog cleanup.

Revision ID: d93f20b51c44
Revises: c82e91a740b3
"""
from alembic import op
import sqlalchemy as sa

revision = "d93f20b51c44"
down_revision = "c82e91a740b3"
branch_labels = None
depends_on = None

AUX_STAGES = ("Pinação", "Pentiação", "Aparação", "Encabação", "Pinação do cabo", "Acabamento", "Acabamentos")

def upgrade():
    conn = op.get_bind()
    # Never destroy historical work silently.
    used_30 = conn.execute(sa.text("""
        SELECT COUNT(*) FROM productions pr JOIN products p ON p.id=pr.product_id
        JOIN holes h ON h.id=p.hole_id WHERE h.quantity=30
    """)).scalar() or 0
    if used_30:
        raise RuntimeError("Existem produções históricas usando produtos de 30 furos. Migração interrompida para preservar os dados.")
    used_aux = conn.execute(sa.text("""
        SELECT COUNT(*) FROM productions pr JOIN stages s ON s.id=pr.stage_id
        WHERE s.name IN ('Pinação','Pentiação','Aparação','Encabação','Pinação do cabo','Acabamento','Acabamentos')
    """)).scalar() or 0
    if used_aux:
        raise RuntimeError("Existem produções históricas em etapas que passariam para Diárias. Migração interrompida para preservar os dados.")

    # Capa Quadrada truly has no holes.
    with op.batch_alter_table("products") as batch:
        batch.alter_column("hole_id", existing_type=sa.Integer(), nullable=True)
    conn.execute(sa.text("""
        UPDATE products SET hole_id=NULL WHERE family_id IN
        (SELECT id FROM product_families WHERE name='Capa Quadrada')
    """))

    # Remove the obsolete 30-hole defaults and auxiliary production stages.
    conn.execute(sa.text("DELETE FROM prices WHERE product_id IN (SELECT p.id FROM products p JOIN holes h ON h.id=p.hole_id WHERE h.quantity=30)"))
    conn.execute(sa.text("DELETE FROM products WHERE hole_id IN (SELECT id FROM holes WHERE quantity=30)"))
    conn.execute(sa.text("DELETE FROM holes WHERE quantity=30"))
    conn.execute(sa.text("DELETE FROM prices WHERE stage_id IN (SELECT id FROM stages WHERE name IN ('Pinação','Pentiação','Aparação','Encabação','Pinação do cabo','Acabamento','Acabamentos'))"))
    conn.execute(sa.text("DELETE FROM stages WHERE name IN ('Pinação','Pentiação','Aparação','Encabação','Pinação do cabo','Acabamento','Acabamentos')"))

    # Correct the current price table once during the version migration. Future
    # manual price changes are not reset by the idempotent seed.
    price_map = {
        ("Básica",16):("2.00","2.00"), ("Extra",16):("2.00","2.00"),
        ("Extra",20):("2.50","2.50"), ("Extra",22):("3.00","3.00"),
        ("Inovada",20):("2.50","2.50"), ("PET",16):("4.00","4.00"),
        ("PET",20):("5.00","5.00"), ("Nailon",16):("2.00","2.00"),
        ("Nailon",20):("2.50","2.50"), ("Cipó",16):("2.50","2.50"),
        ("Cipó",20):("3.00","3.00"), ("Capa Quadrada",None):("1.50","2.50"),
    }
    for (family, hole), (tie, fill) in price_map.items():
        for stage, value in (("Amarração", tie), ("Enchimento", fill)):
            conn.execute(sa.text("""
                UPDATE prices SET price_per_dozen=:value WHERE stage_id=(SELECT id FROM stages WHERE name=:stage)
                AND product_id IN (SELECT p.id FROM products p JOIN product_families f ON f.id=p.family_id
                    WHERE f.name=:family AND ((:hole IS NULL AND p.hole_id IS NULL) OR p.hole_id=(SELECT id FROM holes WHERE quantity=:hole)))
            """), {"value":value,"stage":stage,"family":family,"hole":hole})

    # Daily work value is manual. fraction remains only as legacy/type helper;
    # NULL means another partial period.
    with op.batch_alter_table("daily_works") as batch:
        batch.drop_constraint("ck_daily_work_fraction", type_="check")
        batch.alter_column("fraction", existing_type=sa.Numeric(2,1), nullable=True)
        batch.add_column(sa.Column("period", sa.String(30), nullable=False, server_default="Inteira"))
    conn.execute(sa.text("UPDATE daily_works SET period=CASE WHEN fraction=0.5 THEN 'Meia' ELSE 'Inteira' END"))


def downgrade():
    # Catalog rows are intentionally not recreated with guessed business data.
    with op.batch_alter_table("daily_works") as batch:
        batch.drop_column("period")
        batch.alter_column("fraction", existing_type=sa.Numeric(2,1), nullable=False)
        batch.create_check_constraint("ck_daily_work_fraction", "fraction IN (0.5, 1.0)")
    with op.batch_alter_table("products") as batch:
        batch.alter_column("hole_id", existing_type=sa.Integer(), nullable=False)
