from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.core.database import Base
from webapp.models.student import student_courses

if TYPE_CHECKING:
    from webapp.models.student import Student


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)
    students: Mapped[list["Student"]] = relationship(
        secondary=student_courses, back_populates="courses", lazy="selectin"
    )