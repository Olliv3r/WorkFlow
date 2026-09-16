from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from app.extensions import db
from sqlalchemy import Date, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Advance(db.Model):
    __tablename__ = "advances"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    observation: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    deductions: Mapped[List["AdvanceDeduction"]] = relationship(back_populates="advance", cascade="all, delete-orphan")

    @property
    def deducted_amount(self):
        return sum((d.amount for d in self.deductions), Decimal("0.00"))

    @property
    def balance(self):
        return self.amount - self.deducted_amount

    @property
    def status(self):
        if self.deducted_amount <= 0:
            return "pending"
        if self.balance > 0:
            return "partial"
        return "discounted"
