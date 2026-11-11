from webapp.models.user import User
from webapp.api.deps import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from webapp.api.deps import commit_or_rollback, get_db,require_role
from webapp.models.course import Course
from webapp.models.student import Student
from webapp.schemas.course import CourseCreate, CourseOut

router = APIRouter(tags=["Courses"])


@router.post(
    "/courses", response_model=CourseOut, status_code=status.HTTP_201_CREATED
)
async def create_course(data: CourseCreate, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    course = Course(title=data.title)
    db.add(course)
    await commit_or_rollback(db, "Could not create course")
    await db.refresh(course)
    return course


@router.get("/courses", response_model=list[CourseOut])
async def get_courses(db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    result = await db.scalars(select(Course).order_by(Course.id))
    return result.all()


@router.get("/courses/{course_id}", response_model=CourseOut)
async def get_course(course_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    course = await db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/courses/{course_id}", response_model=CourseOut)
async def update_course(
    course_id: int, data: CourseCreate, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)
):
    course = await db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    course.title = data.title
    await commit_or_rollback(db, "Could not update course")
    await db.refresh(course)
    return course


@router.delete("/courses/{course_id}")
async def delete_course(course_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(require_role("admin"))):
    course = await db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    await db.delete(course)
    await commit_or_rollback(db, "Could not delete course")
    return {"message": "Course deleted"}


# Enrolment endpoints
@router.post("/students/{student_id}/courses/{course_id}")
async def enrol_student(
    student_id: int, course_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)
):
    student = await db.scalar(
        select(Student)
        .options(selectinload(Student.courses))
        .where(Student.id == student_id)
    )
    course = await db.get(Course, course_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    if any(c.id == course_id for c in student.courses):
        raise HTTPException(status_code=409, detail="Student already enrolled")
    student.courses.append(course)
    await commit_or_rollback(db, "Could not enrol student")
    return {"message": "Student enrolled successfully"}


@router.get("/students/{student_id}/courses", response_model=list[CourseOut])
async def get_student_courses(
    student_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)
):
    student = await db.scalar(
        select(Student)
        .options(selectinload(Student.courses))
        .where(Student.id == student_id)
    )
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student.courses


@router.delete("/students/{student_id}/courses/{course_id}")
async def unenrol_student(
    student_id: int, course_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(require_role("admin"))
):
    student = await db.scalar(
        select(Student)
        .options(selectinload(Student.courses))
        .where(Student.id == student_id)
    )
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    course = next((c for c in student.courses if c.id == course_id), None)
    if course is None:
        raise HTTPException(status_code=404, detail="Course enrolment not found")
    student.courses.remove(course)
    await commit_or_rollback(db, "Could not remove enrolment")
    return {"message": "Student unenrolled successfully"}