from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import Optional, List

class Hole(db.Model):
    __tablename__ = "holes"

    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column(String(300))

    products: Mapped[List["Product"]] = relationship(
        back_populates="hole"
    )
