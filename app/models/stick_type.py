from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import Optional, List

class StickType(db.Model):
    __tablename__ = "stick_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(300))

    products: Mapped[List["Product"]] = relationship(
        back_populates="stick_type"
    )
