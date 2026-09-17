from decimal import Decimal
from app.extensions import db
from sqlalchemy import Numeric, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class AdvanceDeduction(db.Model):
    __tablename__ = "advance_deductions"
    __table_args__ = (UniqueConstraint("advance_id", "payment_id", "kind", name="uq_advance_payment_kind_deduction"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    advance_id: Mapped[int] = mapped_column(ForeignKey("advances.id"), index=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    # closing: vale já existente abatido ao criar o fechamento (já refletido em net_amount)
    # receivable: vale criado depois, compensado contra saldo já a receber
    kind: Mapped[str] = mapped_column(String(20), default="closing", server_default="closing", index=True)
    advance: Mapped["Advance"] = relationship(back_populates="deductions")
    payment: Mapped["Payment"] = relationship(back_populates="advance_deductions")
