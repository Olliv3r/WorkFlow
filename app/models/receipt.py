from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from app.extensions import db
from sqlalchemy import Date, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Receipt(db.Model):
    """Dinheiro efetivamente recebido.

    Pode ser criado no contexto de um fechamento (com alocação conhecida) ou
    como recebimento posterior sem origem identificada.
    """
    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    observation: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    allocations: Mapped[List["ReceiptAllocation"]] = relationship(
        back_populates="receipt", cascade="all, delete-orphan"
    )

    @property
    def allocated_amount(self):
        return sum((item.amount for item in self.allocations), Decimal("0.00"))

    @property
    def unallocated_amount(self):
        return self.amount - self.allocated_amount
