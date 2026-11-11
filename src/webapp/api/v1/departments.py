from webapp.api.deps import get_current_user
from webapp.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from webapp.api.deps import commit_or_rollback, get_db,require_role
from webapp.models.department import Department
from webapp.schemas.department import DepartmentCreate, DepartmentOut

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
async def create_department(data: DepartmentCreate, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    department = Department(name=data.name)
    db.add(department)
    await commit_or_rollback(db, "Could not create department")
    await db.refresh(department)
    return department


@router.get("", response_model=list[DepartmentOut])
async def get_departments(db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    result = await db.scalars(
        select(Department)
        .options(selectinload(Department.students))
        .order_by(Department.id)
    )
    return result.all()


@router.get("/{department_id}", response_model=DepartmentOut)
async def get_department(department_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    result = await db.scalars(
        select(Department)
        .options(selectinload(Department.students))
        .where(Department.id == department_id)
    )
    department = result.first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.put("/{department_id}", response_model=DepartmentOut)
async def update_department(
    department_id: int, data: DepartmentCreate, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)
):
    department = await db.get(Department, department_id)
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    department.name = data.name
    await commit_or_rollback(db, "Could not update department")
    result = await db.scalars(
        select(Department)
        .options(selectinload(Department.students))
        .where(Department.id == department_id)
    )
    return result.first()


@router.delete("/{department_id}")
async def delete_department(department_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(require_role('admin'))):
    result = await db.scalars(
        select(Department)
        .options(selectinload(Department.students))
        .where(Department.id == department_id)
    )
    department = result.first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    if department.students:
        raise HTTPException(status_code=409, detail="Move or delete its students first")
    await db.delete(department)
    await commit_or_rollback(db, "Could not delete department")
    return {"message": "Department deleted"}