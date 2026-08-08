from app.extensions import db
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

class ProductFamily(db.Model):
    __tablename__ = 'product_families'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(300))
    active: Mapped[bool] = mapped_column(default=True)
    
    products: Mapped[List["Product"]] = relationship(
        back_populates="family"
    )
