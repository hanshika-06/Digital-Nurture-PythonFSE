import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, Numeric, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Department(Base):
    __tablename__ = "departments"
    
    department_id = Column(Integer, primary_key=True, index=True)
    dept_name = Column(String(100), nullable=False)
    head_of_dept = Column(String(100), nullable=True)
    budget = Column(Float, nullable=True)
    
    students = relationship("Student", back_populates="department")
    courses = relationship("Course", back_populates="department")
    professors = relationship("Professor", back_populates="department")


class Student(Base):
    __tablename__ = "students"
    
    student_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=True)
    enrollment_year = Column(Integer, nullable=False)
    
    # Task 2: is_active column added for Hands-On 07 migrations
    is_active = Column(Boolean, default=True, nullable=False)

    department = relationship("Department", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"
    
    course_id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(150), nullable=False)
    course_code = Column(String(20), unique=True, index=True, nullable=False)
    credits = Column(Integer, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=False)
    
    department = relationship("Department", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    schedules = relationship("CourseSchedule", back_populates="course", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "enrollments"
    
    enrollment_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    enrollment_date = Column(Date, nullable=True)
    grade = Column(String(2), nullable=True)
    
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class Professor(Base):
    __tablename__ = "professors"
    
    professor_id = Column(Integer, primary_key=True, index=True)
    prof_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=True)
    salary = Column(Float, nullable=True)
    
    department = relationship("Department", back_populates="professors")


class CourseSchedule(Base):
    __tablename__ = "course_schedules"
    
    schedule_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    day_of_week = Column(String(20), nullable=False)
    start_time = Column(String(10), nullable=False)
    end_time = Column(String(10), nullable=False)
    
    course = relationship("Course", back_populates="schedules")

# Default database connection string (SQLite fallback)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///college_db_orm.db")
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully.")
