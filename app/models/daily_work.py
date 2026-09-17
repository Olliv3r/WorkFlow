from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from app.extensions import db
from sqlalchemy import Date, Numeric, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class DailyWork(db.Model):
    __tablename__ = "daily_works"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    # Legacy helper: 1=inteira, 0.5=meia, NULL=outro período parcial.
    fraction: Mapped[Optional[Decimal]] = mapped_column(Numeric(2, 1), nullable=True)
    period: Mapped[str] = mapped_column(String(30), default="Inteira")
    # Kept for DB compatibility. From v0.0.11 this is the manually informed
    # occurrence value, not a global full-day rate.
    daily_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    description: Mapped[str] = mapped_column(String(150), default="Serviços variados de auxílio")
    observation: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    payment_id: Mapped[Optional[int]] = mapped_column(ForeignKey("payments.id"), index=True)
    payment: Mapped[Optional["Payment"]] = relationship(back_populates="daily_works")
