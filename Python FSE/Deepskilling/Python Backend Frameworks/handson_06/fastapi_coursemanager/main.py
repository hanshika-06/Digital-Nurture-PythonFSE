from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
)

from database import engine, get_db
from models import Base, Course, Department

app = FastAPI(
    title="Course Management API",
    version="1.0"
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {
        "message": "API running"
    }


@app.post(
    "/api/courses/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_course(course: CourseCreate, db: AsyncSession = Depends(get_db)):
    # Check if code already exists
    code_stmt = select(Course).where(Course.code == course.code)
    code_result = await db.execute(code_stmt)
    if code_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course with code '{course.code}' already exists"
        )

    new_course = Course(
        name=course.name,
        code=course.code,
        credits=course.credits,
        department_id=course.department_id
    )
    db.add(new_course)
    await db.commit()
    await db.refresh(new_course)
    return new_course


@app.get(
    "/api/courses/{course_id}",
    response_model=CourseResponse
)
async def get_course(course_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Course).where(Course.id == course_id)
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return course


@app.get(
    "/api/courses/",
    response_model=List[CourseResponse]
)
async def get_courses(
    skip: int = 0,
    limit: int = 10,
    department_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Course)
    if department_id is not None:
        stmt = stmt.where(Course.department_id == department_id)
        
    stmt = stmt.offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@app.put(
    "/api/courses/{course_id}",
    response_model=CourseResponse
)
async def update_course(
    course_id: int,
    updated_course: CourseUpdate,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Course).where(Course.id == course_id)
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    update_data = updated_course.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(course, key, val)

    await db.commit()
    await db.refresh(course)
    return course


@app.delete(
    "/api/courses/{course_id}"
)
async def delete_course(course_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Course).where(Course.id == course_id)
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    await db.delete(course)
    await db.commit()
    return {
        "message": "Course deleted"
    }


@app.get("/async-demo/")
async def async_demo(
    db: AsyncSession = Depends(get_db)
):
    return {
        "message": "Async database connection successful"
    }