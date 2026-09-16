"""
Preço atual por combinação produto+etapa — editável, sem histórico de
vigência. Decisão explícita: quando o preço muda, este registro é
sobrescrito (UPDATE), o valor anterior não fica guardado em lugar
nenhum. Production.price_per_dozen continua sendo o valor congelado
no momento de cada produção — este model só serve para preencher o
formulário automaticamente ao selecionar produto+etapa, não afeta
produções já registradas.
"""
from __future__ import annotations
from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from decimal import Decimal


class Price(db.Model):
    __tablename__ = "prices"
    __table_args__ = (
        UniqueConstraint(
            "product_id", "stage_id", name="uq_price_product_stage"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    price_per_dozen: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    product: Mapped["Product"] = relationship()
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    stage: Mapped["Stage"] = relationship()
    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"))
