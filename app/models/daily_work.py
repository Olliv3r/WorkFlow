from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from app.extensions import db
from sqlalchemy import Date, Numeric, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

class DailyWork(db.Model):
    __tablename__ = "daily_works"
    __table_args__ = (
        CheckConstraint("fraction IN (0.5, 1.0)", name="ck_daily_work_fraction"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    fraction: Mapped[Decimal] = mapped_column(Numeric(2, 1))
    daily_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    description: Mapped[str] = mapped_column(String(150), default="Acabamentos e serviços auxiliares")
    observation: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    payment_id: Mapped[Optional[int]] = mapped_column(ForeignKey("payments.id"), index=True)
    payment: Mapped[Optional["Payment"]] = relationship(back_populates="daily_works")
