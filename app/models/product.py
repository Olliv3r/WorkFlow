from app.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, ForeignKey
from typing import Optional, List
from datetime import date, datetime

class Product(db.Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    active: Mapped[bool] = mapped_column(default=True)

    family_id: Mapped[int] = mapped_column(
        ForeignKey("product_families.id")
    )
    family: Mapped["ProductFamily"] = relationship(
        back_populates="products"
    )

    material_id: Mapped[int] = mapped_column(
        ForeignKey("materials.id")
    )
    material: Mapped["Material"] = relationship(
        back_populates="products"
    )

    quality_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("qualities.id")
    )
    quality: Mapped[Optional["Quality"]] = relationship(
        back_populates="products"
    )

    hole_id: Mapped[int] = mapped_column(
        ForeignKey("holes.id")
    )
    hole: Mapped["Hole"] = relationship(
        back_populates="products"
    )

    stick_type_id: Mapped[int] = mapped_column(
        ForeignKey("stick_types.id")
    )
    stick_type: Mapped["StickType"] = relationship(
        back_populates="products"
    )
    productions: Mapped[List["Production"]] = relationship(
        back_populates="product"
    )
