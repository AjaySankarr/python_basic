from pydantic import BaseModel, ConfigDict, Field
from webapp.schemas.course import CourseOut


class ProfileCreate(BaseModel):
    address: str
    phone: str = Field(min_length=5, max_length=20)


class ProfileOut(ProfileCreate):
    id: int
    student_id: int

    model_config = ConfigDict(from_attributes=True)


class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=18, le=100)
    department_id: int


class StudentOut(BaseModel):
    id: int
    name: str
    age: int
    department_id: int
    profile: ProfileOut | None = None
    courses: list[CourseOut] = []

    model_config = ConfigDict(from_attributes=True)