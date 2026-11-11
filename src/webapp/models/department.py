from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.core.database import Base

if TYPE_CHECKING:
    from webapp.models.student import Student


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    students: Mapped[list["Student"]] = relationship(
        back_populates="department", lazy="selectin"
    )