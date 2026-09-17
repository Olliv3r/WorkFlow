from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Date, Numeric, Integer
from typing import Optional, List
from datetime import date
from decimal import Decimal

class Payment(db.Model):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_period: Mapped[date] = mapped_column(Date, index=True)
    end_period: Mapped[date] = mapped_column(Date, index=True)

    payment_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    advance_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    net_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total_dozens: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    observation: Mapped[Optional[str]] = mapped_column(Text)

    productions: Mapped[List["Production"]] = relationship(back_populates="payment")
    daily_works: Mapped[List["DailyWork"]] = relationship(back_populates="payment")
    advance_deductions: Mapped[List["AdvanceDeduction"]] = relationship(back_populates="payment", cascade="all, delete-orphan")
    receipt_allocations: Mapped[List["ReceiptAllocation"]] = relationship(back_populates="payment", cascade="all, delete-orphan")

    @property
    def received_amount(self):
        return sum((item.amount for item in self.receipt_allocations), Decimal("0.00"))

    @property
    def receivable_advance_amount(self):
        return sum((item.amount for item in self.advance_deductions if getattr(item, "kind", "closing") == "receivable"), Decimal("0.00"))

    @property
    def pending_amount(self):
        # Deduções feitas no fechamento já reduziram net_amount. Somente vales
        # posteriores (kind=receivable) reduzem novamente o saldo a receber.
        remaining = self.net_amount - self.received_amount - self.receivable_advance_amount
        return remaining if remaining > 0 else Decimal("0.00")

    @property
    def receipt_status(self):
        if self.pending_amount <= 0:
            return "paid"
        if self.received_amount > 0:
            return "partial"
        return "pending"
