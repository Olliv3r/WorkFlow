from decimal import Decimal
from app.extensions import db
from sqlalchemy import Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

class AdvanceDeduction(db.Model):
    __tablename__ = "advance_deductions"
    __table_args__ = (UniqueConstraint("advance_id", "payment_id", name="uq_advance_payment_deduction"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    advance_id: Mapped[int] = mapped_column(ForeignKey("advances.id"), index=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    advance: Mapped["Advance"] = relationship(back_populates="deductions")
    payment: Mapped["Payment"] = relationship(back_populates="advance_deductions")
