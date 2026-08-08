from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, Date
from typing import Optional
from datetime import date, datetime

class Production(db.Model):
    __tablename__ = "productions"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date)
    dozens: Mapped[int] = mapped_column()
    price_per_dozen: Mapped[float] = mapped_column(default=2.0)
    total_amount: Mapped[int] = mapped_column()
    observation: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    product: Mapped["Product"] = relationship(
        back_populates="productions"
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    stage: Mapped["Stage"] = relationship(
        back_populates="productions"
    )
    stage_id: Mapped[int] = mapped_column(
        ForeignKey("stages.id")
    )

    payment: Mapped[Optional["Payment"]] = relationship(
        back_populates="productions"
    )
    payment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("payments.id")
    )
