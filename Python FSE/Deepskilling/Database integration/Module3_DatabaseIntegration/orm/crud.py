import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from models import Base, Department, Student, Course, Enrollment, Professor

# Connect to database using standard echo=True to observe SQL logging
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///college_db_orm.db")

# Delete local DB if exists for clean CRUD logs demonstration
if "sqlite" in DATABASE_URL:
    db_file = DATABASE_URL.replace("sqlite:///", "")
    if os.path.exists(db_file):
        try: os.remove(db_file)
        except: pass

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

def run_orm_crud_operations():
    # 79. Initialize database tables
    Base.metadata.create_all(engine)
    
    print("\n--- Step 81: INSERT Departments & Students ---")
    d1 = Department(dept_name="Computer Science", head_of_dept="Dr. Ramesh Kumar", budget=850000.0)
    d2 = Department(dept_name="Electronics", head_of_dept="Dr. Priya Nair", budget=620000.0)
    d3 = Department(dept_name="Mechanical", head_of_dept="Dr. Suresh Iyer", budget=540000.0)
    session.add_all([d1, d2, d3])
    session.commit()
    
    s1 = Student(first_name="Arjun", last_name="Mehta", email="arjun.mehta@college.edu", enrollment_year=2022, department_id=d1.department_id)
    s2 = Student(first_name="Priya", last_name="Suresh", email="priya.suresh@college.edu", enrollment_year=2022, department_id=d1.department_id)
    s3 = Student(first_name="Rohan", last_name="Verma", email="rohan.verma@college.edu", enrollment_year=2021, department_id=d2.department_id)
    s4 = Student(first_name="Sneha", last_name="Patel", email="sneha.patel@college.edu", enrollment_year=2023, department_id=d3.department_id)
    s5 = Student(first_name="Vikram", last_name="Das", email="vikram.das@college.edu", enrollment_year=2022, department_id=d1.department_id)
    session.add_all([s1, s2, s3, s4, s5])
    session.commit()
    
    print("\n--- Step 82: INSERT Courses & Enrollments ---")
    c1 = Course(course_name="Data Structures & Algorithms", course_code="CS101", credits=4, department_id=d1.department_id)
    c2 = Course(course_name="Database Management Systems", course_code="CS102", credits=3, department_id=d1.department_id)
    c3 = Course(course_name="Circuit Theory", course_code="EC101", credits=3, department_id=d2.department_id)
    session.add_all([c1, c2, c3])
    session.commit()
    
    e1 = Enrollment(student_id=s1.student_id, course_id=c1.course_id, enrollment_date=datetime.date(2022, 7, 1), grade="A")
    e2 = Enrollment(student_id=s1.student_id, course_id=c2.course_id, enrollment_date=datetime.date(2022, 7, 1), grade="B")
    e3 = Enrollment(student_id=s2.student_id, course_id=c1.course_id, enrollment_date=datetime.date(2022, 7, 1), grade="B")
    e4 = Enrollment(student_id=s3.student_id, course_id=c3.course_id, enrollment_date=datetime.date(2021, 7, 1), grade="A")
    session.add_all([e1, e2, e3, e4])
    session.commit()
    
    print("\n--- Step 83: READ Students in Computer Science ---")
    cs_students = session.query(Student).join(Department).filter(Department.dept_name == "Computer Science").all()
    print(f"Students in CS department ({len(cs_students)} found):")
    for student in cs_students:
         print(f" - {student.first_name} {student.last_name}")

    print("\n--- Step 84: READ All Enrollments (N+1 demonstration) ---")
    # Fetch all enrollments (lazy-loaded by default)
    # This loop triggers individual SQL queries to fetch Student and Course per enrollment row.
    print("Executing loop that triggers database queries for each row:")
    enrollments_lazy = session.query(Enrollment).all()
    for e in enrollments_lazy:
        print(f" - Student: {e.student.first_name} {e.student.last_name} enrolled in Course: {e.course.course_name}")

    print("\n--- Step 85: UPDATE Student enrollment_year ---")
    target_student = session.query(Student).filter(Student.email == "arjun.mehta@college.edu").first()
    if target_student:
        print(f"Updating enrollment year for {target_student.first_name} from {target_student.enrollment_year} to 2023.")
        target_student.enrollment_year = 2023
        session.commit()

    print("\n--- Step 86: DELETE Enrollment ---")
    enrollment_to_delete = session.query(Enrollment).filter(Enrollment.student_id == s1.student_id, Enrollment.course_id == c2.course_id).first()
    if enrollment_to_delete:
        print(f"Removing enrollment record: {enrollment_to_delete.enrollment_id}")
        session.delete(enrollment_to_delete)
        session.commit()
        
    # Check deletion
    check_delete = session.query(Enrollment).filter(Enrollment.student_id == s1.student_id, Enrollment.course_id == c2.course_id).first()
    print(f"Verify deletion: {'Success' if check_delete is None else 'Failed'}")


def run_joined_load_demonstration():
    print("\n=====================================================================")
    print("Task 3: Eager Loading using joinedload to Fix N+1 (Step 87-90)")
    print("=====================================================================")
    
    # 88. Rewrite query using joinedload
    # This loads all enrollment, student, and course details in exactly 1 single SQL SELECT with INNER JOINs.
    print("Executing Eager Load query (exactly 1 SQL query should be issued):")
    results = session.query(Enrollment).options(
        joinedload(Enrollment.student),
        joinedload(Enrollment.course)
    ).all()
    
    for r in results:
        print(f" - Eager fetched: {r.student.first_name} {r.student.last_name} -> {r.course.course_name}")

if __name__ == "__main__":
    run_orm_crud_operations()
    run_joined_load_demonstration()

"""
================================================================================
ORM N+1 EXPLANATION & TUNING (Step 90)
================================================================================
1. Query count difference:
   - Lazy Load Version (Task 2): Issued 1 query to fetch enrollments list, plus 2 queries 
     (one for Student and one for Course) per row. With 4 enrollments, this resulted 
     in 1 + (4 * 2) = 9 total queries issued. For 10,000 enrollments, this would issue 
     20,001 SQL queries (N+1 problem).
   - Eager Load Version (Task 3): Issued exactly 1 single query using SQL JOINs to fetch 
     all data (Enrollments, Student, Course) in a single database round-trip.
================================================================================
"""
