from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Date
from typing import Optional, List
from datetime import date

class Payment(db.Model):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_period: Mapped[date] = mapped_column(Date)
    end_period: Mapped[date] = mapped_column(Date)

    payment_date: Mapped[Optional[date]] = mapped_column(Date)
    total_amount: Mapped[int] = mapped_column(default=0)
    total_dozens: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    observation: Mapped[Optional[str]] = mapped_column(Text)

    productions: Mapped[List["Production"]] = relationship(
        back_populates="payment"
    )
