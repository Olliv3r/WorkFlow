from decimal import Decimal
from app.extensions import db
from sqlalchemy import Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ReceiptAllocation(db.Model):
    __tablename__ = "receipt_allocations"
    __table_args__ = (
        UniqueConstraint("receipt_id", "payment_id", name="uq_receipt_payment_allocation"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.id"), index=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    receipt: Mapped["Receipt"] = relationship(back_populates="allocations")
    payment: Mapped["Payment"] = relationship(back_populates="receipt_allocations")
