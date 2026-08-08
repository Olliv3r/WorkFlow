from app.extensions import db
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

class Stage(db.Model):
    __tablename__ = 'stages'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(300))

    order: Mapped[int] = mapped_column(default=1)
    active: Mapped[bool] = mapped_column(default=True)
    
    productions: Mapped[List["Production"]] = relationship(
        back_populates="stage"
    )

