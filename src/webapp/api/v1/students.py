from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from webapp.api.deps import commit_or_rollback, get_current_user, get_db, require_role
from webapp.models.department import Department
from webapp.models.student import Student, StudentProfile
from webapp.models.user import User
from webapp.schemas.student import (
    ProfileCreate,
    ProfileOut,
    StudentCreate,
    StudentOut,
)

router = APIRouter(prefix="/students", tags=["Students"])


def student_query():
    return select(Student).options(
        selectinload(Student.profile), selectinload(Student.courses)
    )


@router.post("", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
async def create_student(data: StudentCreate, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    if await db.get(Department, data.department_id) is None:
        raise HTTPException(status_code=404, detail="Department not found")
    student = Student(
        name=data.name, age=data.age, department_id=data.department_id
    )
    db.add(student)
    await commit_or_rollback(db, "Could not create student")
    result = await db.scalars(student_query().where(Student.id == student.id))
    return result.first()


@router.get("", response_model=list[StudentOut])
async def get_students(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    result = await db.scalars(student_query().order_by(Student.id))
    return result.all()


@router.get("/{student_id}", response_model=StudentOut)
async def get_student(student_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    result = await db.scalars(
        student_query().where(Student.id == student_id)
    )
    student = result.first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=StudentOut)
async def update_student(
    student_id: int, data: StudentCreate, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)
):
    student = await db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    if await db.get(Department, data.department_id) is None:
        raise HTTPException(status_code=404, detail="Department not found")
    student.name, student.age, student.department_id = (
        data.name,
        data.age,
        data.department_id,
    )
    await commit_or_rollback(db, "Could not update student")
    result = await db.scalars(
        student_query().where(Student.id == student_id)
    )
    return result.first()


@router.delete("/{student_id}")
async def delete_student(student_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    student = await db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    await db.delete(student)
    await commit_or_rollback(db, "Could not delete student")
    return {"message": "Student deleted"}


# Profile endpoints
@router.post(
    "/{student_id}/profile",
    response_model=ProfileOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    student_id: int, data: ProfileCreate, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)
):
    student = await db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    existing = await db.scalar(
        select(StudentProfile).where(StudentProfile.student_id == student_id)
    )
    if existing is not None:
        raise HTTPException(
            status_code=409, detail="Student already has a profile"
        )
    profile = StudentProfile(
        student_id=student_id, address=data.address, phone=data.phone
    )
    db.add(profile)
    await commit_or_rollback(db, "Could not create profile")
    await db.refresh(profile)
    return profile


@router.get("/{student_id}/profile", response_model=ProfileOut)
async def get_profile(student_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    profile = await db.scalar(
        select(StudentProfile).where(StudentProfile.student_id == student_id)
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/{student_id}/profile", response_model=ProfileOut)
async def update_profile(
    student_id: int, data: ProfileCreate, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)
):
    profile = await db.scalar(
        select(StudentProfile).where(StudentProfile.student_id == student_id)
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile.address, profile.phone = data.address, data.phone
    await commit_or_rollback(db, "Could not update profile")
    await db.refresh(profile)
    return profile


@router.delete("/{student_id}/profile")
async def delete_profile(student_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(require_role("admin","staff"))):
    profile = await db.scalar(
        select(StudentProfile).where(StudentProfile.student_id == student_id)
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    await db.delete(profile)
    await commit_or_rollback(db, "Could not delete profile")
    return {"message": "Profile deleted"}