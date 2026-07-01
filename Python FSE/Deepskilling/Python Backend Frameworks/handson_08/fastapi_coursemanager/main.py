import math
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

# Local imports
from database import engine, get_db
from models import Base, Department, Course, Student, Enrollment
from schemas import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentDetailResponse,
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    PaginatedCourseResponse,
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    EnrollmentCreate,
    EnrollmentUpdate,
    EnrollmentResponse,
)

app = FastAPI(
    title="Course Management API",
    description="Refactored Course Management REST API with RESTful best practices",
    version="3.0",
    contact={
        "name": "Admin",
        "email": "admin@example.com"
    }
)

# -----------------------------------------------------------------------------
# Database Setup Event
# -----------------------------------------------------------------------------
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        # Automatically creates tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)


# -----------------------------------------------------------------------------
# Standardized Error Exception Handlers
# -----------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
    }
    code = code_map.get(exc.status_code, "ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": exc.detail,
                "field": None
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if errors:
        first_err = errors[0]
        # Extract path to field
        field = ".".join(str(loc) for loc in first_err.get("loc", []))
        message = first_err.get("msg", "Validation error")
    else:
        field = None
        message = "Validation error"
        
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": message,
                "field": field
            }
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "field": None
            }
        }
    )


# -----------------------------------------------------------------------------
# API Versioning discussion comment
# -----------------------------------------------------------------------------
"""
================================================================================
VERSIONING STRATEGIES COMPARISON (Task 2, Step 82)
================================================================================
Two main versioning strategies are commonly used in RESTful API design:

1. URL path versioning (e.g., /api/v1/courses/)
   - Description: The version is embedded directly in the path component of the URL.
   - Pros: 
     * Simple, highly visible, and very easy to test/debug directly in a browser.
     * Easy to route via API Gateways or load balancers based on the URL path.
   - Cons:
     * Violates URI purity conceptually, as the same resource (e.g., a specific course) 
       technically has a different URI when the API version updates.

2. Header-based / Media type versioning (e.g., Accept: application/vnd.api+json;version=1)
   - Description: The client specifies the requested version in a custom header 
     or the standard Accept/Content-Type headers.
   - Pros:
     * Keeps URLs clean and pure, strictly identifying resource identity.
     * Allows semantic version negotiation between client and server.
   - Cons:
     * Harder to test and debug because browsers cannot easily append custom headers 
       without extensions.
     * Web caching proxies may need to use Vary headers to distinguish responses, 
       increasing implementation complexity.
================================================================================
"""


# -----------------------------------------------------------------------------
# Route Definitions (prefixed with /api/v1)
# -----------------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "API running"
    }


# --- Department Routes (for testing support) ---

@app.post(
    "/api/v1/departments/",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Departments"]
)
async def create_department(
    dept_in: DepartmentCreate,
    response: Response,
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
    
    response.headers["Location"] = f"/api/v1/departments/{dept.id}/"
    return dept

@app.get(
    "/api/v1/departments/",
    response_model=List[DepartmentResponse],
    tags=["Departments"]
)
async def get_departments(db: AsyncSession = Depends(get_db)):
    stmt = select(Department)
    result = await db.execute(stmt)
    return result.scalars().all()

@app.get(
    "/api/v1/departments/{dept_id}/",
    response_model=DepartmentDetailResponse,
    tags=["Departments"]
)
async def get_department(dept_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Department).where(Department.id == dept_id)
    result = await db.execute(stmt)
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail=f"Department with id {dept_id} does not exist")
    return dept


# --- Course Routes ---

@app.post(
    "/api/v1/courses/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Courses"],
    summary="Create Course",
    response_description="Course Created Successfully"
)
async def create_course(
    course: CourseCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
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
    
    response.headers["Location"] = f"/api/v1/courses/{new_course.id}/"
    return new_course


@app.get(
    "/api/v1/courses/{course_id}/",
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
            detail=f"Course with id {course_id} does not exist"
        )
    return course


@app.get(
    "/api/v1/courses/",
    response_model=PaginatedCourseResponse,
    tags=["Courses"]
)
async def get_courses(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    department_id: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    if page < 1:
        raise HTTPException(status_code=400, detail="Page number must be 1 or greater")
    if page_size < 1:
        raise HTTPException(status_code=400, detail="Page size must be 1 or greater")

    # Base query
    stmt = select(Course)
    
    # Filtering by department_id
    if department_id is not None:
        stmt = stmt.where(Course.department_id == department_id)
        
    # Search filtering (case-insensitive LIKE search on name and code)
    if search:
        search_filter = f"%{search}%"
        stmt = stmt.where(
            or_(
                Course.name.ilike(search_filter),
                Course.code.ilike(search_filter)
            )
        )
        
    # Count query
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_res = await db.execute(count_stmt)
    total = count_res.scalar() or 0
    
    # Pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    
    res = await db.execute(stmt)
    courses_list = res.scalars().all()
    
    # Calculate next/previous links
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    base_url = str(request.base_url).rstrip('/') + request.url.path
    
    # Add other parameters back to pagination link
    extra_params = []
    if department_id is not None:
        extra_params.append(f"department_id={department_id}")
    if search:
        extra_params.append(f"search={search}")
    extra_params_str = "&" + "&".join(extra_params) if extra_params else ""
    
    next_url = None
    if page < total_pages:
        next_url = f"{base_url}?page={page + 1}&page_size={page_size}{extra_params_str}"
        
    prev_url = None
    if page > 1:
        prev_url = f"{base_url}?page={page - 1}&page_size={page_size}{extra_params_str}"
        
    return {
        "count": total,
        "next": next_url,
        "previous": prev_url,
        "results": courses_list
    }


@app.put(
    "/api/v1/courses/{course_id}/",
    response_model=CourseResponse,
    tags=["Courses"]
)
async def update_course(
    course_id: int,
    updated: CourseCreate, # PUT requires full model
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Course).where(Course.id == course_id)
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} does not exist"
        )
        
    # Check department exists
    dept_stmt = select(Department).where(Department.id == updated.department_id)
    dept_result = await db.execute(dept_stmt)
    if not dept_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with id {updated.department_id} does not exist"
        )
        
    # Check code unique constraint if changing code
    if course.code != updated.code:
        code_stmt = select(Course).where(Course.code == updated.code)
        code_result = await db.execute(code_stmt)
        if code_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course with code '{updated.code}' already exists"
            )

    course.name = updated.name
    course.code = updated.code
    course.credits = updated.credits
    course.department_id = updated.department_id
    
    await db.commit()
    await db.refresh(course)
    return course


@app.patch(
    "/api/v1/courses/{course_id}/",
    response_model=CourseResponse,
    tags=["Courses"]
)
async def patch_course(
    course_id: int,
    updated: CourseUpdate, # PATCH permits optional fields
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Course).where(Course.id == course_id)
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} does not exist"
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
            
    if "code" in update_data and update_data["code"] != course.code:
        code_stmt = select(Course).where(Course.code == update_data["code"])
        code_result = await db.execute(code_stmt)
        if code_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course with code '{update_data['code']}' already exists"
            )

    for key, val in update_data.items():
        setattr(course, key, val)
        
    await db.commit()
    await db.refresh(course)
    return course


@app.delete(
    "/api/v1/courses/{course_id}/",
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
            detail=f"Course with id {course_id} does not exist"
        )
    await db.delete(course)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Student Routes ---

@app.get(
    "/api/v1/students/",
    response_model=List[StudentResponse],
    tags=["Students"]
)
async def get_students(db: AsyncSession = Depends(get_db)):
    stmt = select(Student)
    result = await db.execute(stmt)
    return result.scalars().all()


@app.post(
    "/api/v1/students/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Students"]
)
async def create_student(
    student: StudentCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    # Check email unique constraint
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
    
    response.headers["Location"] = f"/api/v1/students/{new_student.id}/"
    return new_student


@app.get(
    "/api/v1/students/{student_id}/",
    response_model=StudentResponse,
    tags=["Students"]
)
async def get_student(student_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} does not exist"
        )
    return student


@app.put(
    "/api/v1/students/{student_id}/",
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
            detail=f"Student with id {student_id} does not exist"
        )
        
    if student.email != updated.email:
        email_stmt = select(Student).where(Student.email == updated.email)
        email_res = await db.execute(email_stmt)
        if email_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with email '{updated.email}' already exists"
            )

    student.first_name = updated.first_name
    student.last_name = updated.last_name
    student.email = updated.email
    student.enrollment_year = updated.enrollment_year
    
    await db.commit()
    await db.refresh(student)
    return student


@app.patch(
    "/api/v1/students/{student_id}/",
    response_model=StudentResponse,
    tags=["Students"]
)
async def patch_student(
    student_id: int,
    updated: StudentUpdate,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} does not exist"
        )
        
    update_data = updated.model_dump(exclude_unset=True)
    
    if "email" in update_data and update_data["email"] != student.email:
        email_stmt = select(Student).where(Student.email == update_data["email"])
        email_res = await db.execute(email_stmt)
        if email_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with email '{update_data['email']}' already exists"
            )

    for key, val in update_data.items():
        setattr(student, key, val)
        
    await db.commit()
    await db.refresh(student)
    return student


@app.delete(
    "/api/v1/students/{student_id}/",
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
            detail=f"Student with id {student_id} does not exist"
        )
    await db.delete(student)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Enrollment Routes ---

def send_confirmation_email(email: str):
    # Simulated email confirmation output
    print(f"Sending confirmation to {email}")


@app.get(
    "/api/v1/enrollments/",
    response_model=List[EnrollmentResponse],
    tags=["Enrollments"]
)
async def get_enrollments(db: AsyncSession = Depends(get_db)):
    stmt = select(Enrollment)
    result = await db.execute(stmt)
    return result.scalars().all()


@app.post(
    "/api/v1/enrollments/",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Enrollments"]
)
async def create_enrollment(
    enrollment: EnrollmentCreate,
    response: Response,
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
            detail=f"Student with id {enrollment.student_id} does not exist"
        )
        
    # Verify course exists
    course_stmt = select(Course).where(Course.id == enrollment.course_id)
    course_res = await db.execute(course_stmt)
    course = course_res.scalar_one_or_none()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course with id {enrollment.course_id} does not exist"
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
        
    response.headers["Location"] = f"/api/v1/enrollments/{new_enrollment.id}/"
    return new_enrollment


@app.get(
    "/api/v1/enrollments/{enrollment_id}/",
    response_model=EnrollmentResponse,
    tags=["Enrollments"]
)
async def get_enrollment(enrollment_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Enrollment).where(Enrollment.id == enrollment_id)
    result = await db.execute(stmt)
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment with id {enrollment_id} does not exist"
        )
    return enrollment


@app.delete(
    "/api/v1/enrollments/{enrollment_id}/",
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
            detail=f"Enrollment with id {enrollment_id} does not exist"
        )
    await db.delete(enrollment)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Get Students Enrolled in a Course ---

@app.get(
    "/api/v1/courses/{course_id}/students/",
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
            detail=f"Course with id {course_id} does not exist"
        )
        
    stmt = select(Student).join(Enrollment).where(Enrollment.course_id == course_id)
    result = await db.execute(stmt)
    return result.scalars().all()