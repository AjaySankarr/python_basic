from fastapi import APIRouter

from webapp.api.v1.auth import router as auth_router
from webapp.api.v1.courses import router as courses_router
from webapp.api.v1.departments import router as departments_router
from webapp.api.v1.students import router as students_router
from webapp.api.v1.files import router as files_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(departments_router)
api_router.include_router(students_router)
api_router.include_router(courses_router)
api_router.include_router(files_router)