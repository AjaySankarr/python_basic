from pydantic import BaseModel, ConfigDict, Field
from webapp.schemas.student import StudentOut


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class DepartmentOut(DepartmentCreate):
    id: int
    students: list[StudentOut] = []

    model_config = ConfigDict(from_attributes=True)