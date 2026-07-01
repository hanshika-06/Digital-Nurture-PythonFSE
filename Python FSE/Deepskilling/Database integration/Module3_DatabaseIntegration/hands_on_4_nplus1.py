import sqlite3
import time

def setup_database():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE students (
        student_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL
    );
    """)
    cursor.execute("""
    CREATE TABLE enrollments (
        enrollment_id INTEGER PRIMARY KEY,
        student_id INTEGER NOT NULL,
        course_name TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)
    
    # Insert mock students (8 students)
    students_data = [
        ("Arjun", "Mehta"),
        ("Priya", "Suresh"),
        ("Rohan", "Verma"),
        ("Sneha", "Patel"),
        ("Vikram", "Das"),
        ("Kavya", "Menon"),
        ("Aditya", "Singh"),
        ("Deepika", "Rao")
    ]
    cursor.executemany("INSERT INTO students (first_name, last_name) VALUES (?, ?)", students_data)
    
    # Insert 12 mock enrollments
    enrollments_data = [
        (1, "Data Structures & Algorithms"),
        (1, "Database Management Systems"),
        (2, "Data Structures & Algorithms"),
        (2, "Object Oriented Programming"),
        (3, "Circuit Theory"),
        (4, "Thermodynamics"),
        (5, "Data Structures & Algorithms"),
        (5, "Database Management Systems"),
        (6, "Circuit Theory"),
        (7, "Thermodynamics"),
        (8, "Data Structures & Algorithms"),
        (8, "Object Oriented Programming")
    ]
    cursor.executemany("INSERT INTO enrollments (student_id, course_name) VALUES (?, ?)", enrollments_data)
    conn.commit()
    return conn

# Custom connection wrapper to count queries
class QueryCounter:
    def __init__(self, conn):
        self.conn = conn
        self.count = 0

    def execute(self, query, params=()):
        self.count += 1
        return self.conn.execute(query, params)


def run_nplus1_simulation():
    # 56. Simulate the N+1 problem in Python
    conn = setup_database()
    counter = QueryCounter(conn)
    
    start_time = time.perf_counter()
    
    # Query 1: Fetch all enrollments
    cursor = counter.execute("SELECT enrollment_id, student_id, course_name FROM enrollments")
    enrollments = cursor.fetchall()
    
    results = []
    # Queries 2 to N+1: Fetch student name for each enrollment
    for enrollment in enrollments:
        enrollment_id, student_id, course_name = enrollment
        student_cursor = counter.execute("SELECT first_name, last_name FROM students WHERE student_id = ?", (student_id,))
        student = student_cursor.fetchone()
        results.append({
            "enrollment_id": enrollment_id,
            "student_name": f"{student[0]} {student[1]}",
            "course_name": course_name
        })
        
    duration = time.perf_counter() - start_time
    print(f"--- N+1 Version ---")
    print(f"Total queries executed: {counter.count}")
    print(f"Time taken: {duration:.6f} seconds")
    print(f"Results fetched count: {len(results)}")
    
    conn.close()

def run_optimized_simulation():
    # 57. Rewrite the script using a single JOIN query
    conn = setup_database()
    counter = QueryCounter(conn)
    
    start_time = time.perf_counter()
    
    # Query 1: Fetch all enrollments with student names in a single JOIN
    query = """
    SELECT e.enrollment_id, s.first_name, s.last_name, e.course_name 
    FROM enrollments e
    INNER JOIN students s ON e.student_id = s.student_id
    """
    cursor = counter.execute(query)
    rows = cursor.fetchall()
    
    results = []
    for row in rows:
        enrollment_id, first_name, last_name, course_name = row
        results.append({
            "enrollment_id": enrollment_id,
            "student_name": f"{first_name} {last_name}",
            "course_name": course_name
        })
        
    duration = time.perf_counter() - start_time
    print(f"\n--- Optimized Single-Join Version ---")
    print(f"Total queries executed: {counter.count}")
    print(f"Time taken: {duration:.6f} seconds")
    print(f"Results fetched count: {len(results)}")
    
    conn.close()

if __name__ == "__main__":
    run_nplus1_simulation()
    run_optimized_simulation()

"""
================================================================================
N+1 PROBLEM ANALYSIS & COMPARISON (Step 58 & 59)
================================================================================
1. Database Round-Trips Comparison:
   - In the N+1 version, fetching 12 enrollments required 13 database queries (1 query to 
     retrieve the list of enrollments, and 12 individual queries to fetch student names).
   - In the optimized version, the same results were fetched using exactly 1 query 
     with an INNER JOIN.

2. Impact on a Real Application with 10,000 Enrollments:
   - The N+1 version would issue: 1 (initial query) + 10,000 (individual lookups) = 10,001 queries.
   - The optimized version would still issue only 1 query.
   - Extra queries issued by the N+1 version: 10,000 extra queries.
   - In production, this would cause massive network latency overhead, database lock congestion, 
     and CPU exhaustion, leading to extremely slow response times.
================================================================================
"""
