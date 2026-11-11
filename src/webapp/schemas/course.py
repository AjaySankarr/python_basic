from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    title: str = Field(min_length=2, max_length=100)


class CourseOut(CourseCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)