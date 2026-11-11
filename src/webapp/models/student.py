from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String, Table,Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.core.database import Base

if TYPE_CHECKING:
    from webapp.models.course import Course
    from webapp.models.department import Department

student_courses = Table(
    "student_courses",
    Base.metadata,
    Column(
        "student_id",
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "course_id",
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column(Integer)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    department: Mapped["Department"] = relationship(
        back_populates="students", lazy="selectin"
    )
    profile: Mapped["StudentProfile | None"] = relationship(
        back_populates="student",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    courses: Mapped[list["Course"]] = relationship(
        secondary=student_courses, back_populates="students", lazy="selectin"
    )


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), unique=True
    )
    address: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str] = mapped_column(String(20))
    student: Mapped[Student] = relationship(
        back_populates="profile", lazy="selectin"
    )