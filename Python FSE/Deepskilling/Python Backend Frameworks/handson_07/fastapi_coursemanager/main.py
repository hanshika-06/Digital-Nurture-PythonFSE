from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from database import engine, get_db
from models import Base, Department, Course, Student, Enrollment
from schemas import (
    DepartmentCreate,
    DepartmentResponse,
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    EnrollmentCreate,
    EnrollmentResponse,
)

app = FastAPI(
    title="Course Management API",
    description="Course Management REST API using FastAPI",
    version="2.0",
    contact={
        "name": "Admin",
        "email": "admin@example.com"
    }
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


# --- Department Routes (for testing support) ---

@app.post(
    "/api/departments/",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Departments"]
)
async def create_department(
    dept_in: DepartmentCreate,
    db: AsyncSession = Depends(get_db)
):
    dept = Department(
        name=dept_in.name,
        head_of_dept=dept_in.head_of_dept,
        budget=dept_in.budget
    )
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept

@app.get(
    "/api/departments/",
    response_model=List[DepartmentResponse],
    tags=["Departments"]
)
async def get_departments(db: AsyncSession = Depends(get_db)):
    stmt = select(Department)
    result = await db.execute(stmt)
    return result.scalars().all()


# --- Course Routes ---

@app.post(
    "/api/courses/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Courses"],
    summary="Create Course",
    response_description="Course Created Successfully"
)
async def create_course(course: CourseCreate, db: AsyncSession = Depends(get_db)):
    # Verify department exists
    dept_stmt = select(Department).where(Department.id == course.department_id)
    dept_result = await db.execute(dept_stmt)
    if not dept_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with id {course.department_id} does not exist"
        )
        
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
    response_model=CourseResponse,
    tags=["Courses"]
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
    response_model=List[CourseResponse],
    tags=["Courses"]
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
    response_model=CourseResponse,
    tags=["Courses"]
)
async def update_course(
    course_id: int,
    updated: CourseUpdate,
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
        
    update_data = updated.model_dump(exclude_unset=True)
    
    if "department_id" in update_data:
        dept_stmt = select(Department).where(Department.id == update_data["department_id"])
        dept_result = await db.execute(dept_stmt)
        if not dept_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with id {update_data['department_id']} does not exist"
            )

    for key, val in update_data.items():
        setattr(course, key, val)
        
    await db.commit()
    await db.refresh(course)
    return course


@app.delete(
    "/api/courses/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Courses"]
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
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Student Routes ---

@app.get(
    "/api/students/",
    response_model=List[StudentResponse],
    tags=["Students"]
)
async def get_students(db: AsyncSession = Depends(get_db)):
    stmt = select(Student)
    result = await db.execute(stmt)
    return result.scalars().all()


@app.post(
    "/api/students/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Students"]
)
async def create_student(
    student: StudentCreate,
    db: AsyncSession = Depends(get_db)
):
    email_stmt = select(Student).where(Student.email == student.email)
    email_res = await db.execute(email_stmt)
    if email_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with email '{student.email}' already exists"
        )
        
    new_student = Student(
        first_name=student.first_name,
        last_name=student.last_name,
        email=student.email,
        enrollment_year=student.enrollment_year
    )
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)
    return new_student


@app.put(
    "/api/students/{student_id}",
    response_model=StudentResponse,
    tags=["Students"]
)
async def update_student(
    student_id: int,
    updated: StudentCreate,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
        
    student.first_name = updated.first_name
    student.last_name = updated.last_name
    student.email = updated.email
    student.enrollment_year = updated.enrollment_year
    
    await db.commit()
    await db.refresh(student)
    return student


@app.delete(
    "/api/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Students"]
)
async def delete_student(student_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    await db.delete(student)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Enrollment Routes ---

def send_confirmation_email(email: str):
    print(f"Sending confirmation to {email}")


@app.get(
    "/api/enrollments/",
    response_model=List[EnrollmentResponse],
    tags=["Enrollments"]
)
async def get_enrollments(db: AsyncSession = Depends(get_db)):
    stmt = select(Enrollment)
    result = await db.execute(stmt)
    return result.scalars().all()


@app.post(
    "/api/enrollments/",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Enrollments"]
)
async def create_enrollment(
    enrollment: EnrollmentCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # Verify student exists
    student_stmt = select(Student).where(Student.id == enrollment.student_id)
    student_res = await db.execute(student_stmt)
    student = student_res.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student not found"
        )
        
    # Verify course exists
    course_stmt = select(Course).where(Course.id == enrollment.course_id)
    course_res = await db.execute(course_stmt)
    if not course_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course not found"
        )
        
    # Check if duplicate enrollment
    uq_stmt = select(Enrollment).where(
        and_(
            Enrollment.student_id == enrollment.student_id,
            Enrollment.course_id == enrollment.course_id
        )
    )
    uq_res = await db.execute(uq_stmt)
    if uq_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is already enrolled in this course"
        )

    new_enrollment = Enrollment(
        student_id=enrollment.student_id,
        course_id=enrollment.course_id,
        grade=enrollment.grade
    )
    db.add(new_enrollment)
    await db.commit()
    await db.refresh(new_enrollment)
    
    # Send email in background
    if student.email:
        background_tasks.add_task(send_confirmation_email, student.email)
        
    return new_enrollment


@app.delete(
    "/api/enrollments/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Enrollments"]
)
async def delete_enrollment(enrollment_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Enrollment).where(Enrollment.id == enrollment_id)
    result = await db.execute(stmt)
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    await db.delete(enrollment)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Get Students Enrolled in a Course ---

@app.get(
    "/api/courses/{course_id}/students/",
    response_model=List[StudentResponse],
    tags=["Courses"]
)
async def get_course_students(course_id: int, db: AsyncSession = Depends(get_db)):
    # Verify course exists
    course_stmt = select(Course).where(Course.id == course_id)
    course_res = await db.execute(course_stmt)
    if not course_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
        
    stmt = select(Student).join(Enrollment).where(Enrollment.course_id == course_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@app.get("/async-demo/")
async def async_demo(
    db: AsyncSession = Depends(get_db)
):
    return {
        "message": "Async database connection successful"
    }