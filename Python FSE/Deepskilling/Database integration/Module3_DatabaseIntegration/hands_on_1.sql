-- =============================================================================
-- HANDS-ON 1: Schema Design & Core SQL — DDL and Normalisation
-- =============================================================================

-- Task 1: Create the Database and Tables
-- Note: Create the database 'college_db' first in your SQL client:
-- CREATE DATABASE college_db;

-- 1. departments table
CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY, -- In PostgreSQL use: department_id SERIAL PRIMARY KEY
    dept_name VARCHAR(100) NOT NULL,
    hod_name VARCHAR(100),
    budget DECIMAL(12,2)
);

-- 2. students table
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY, -- In PostgreSQL use: student_id SERIAL PRIMARY KEY
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    date_of_birth DATE,
    department_id INT,
    enrollment_year INT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- 3. courses table
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY, -- In PostgreSQL use: course_id SERIAL PRIMARY KEY
    course_name VARCHAR(150) NOT NULL,
    course_code VARCHAR(20) UNIQUE,
    credits INT,
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- 4. enrollments table
CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY, -- In PostgreSQL use: enrollment_id SERIAL PRIMARY KEY
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrollment_date DATE,
    grade CHAR(2),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- 5. professors table
CREATE TABLE professors (
    professor_id INT AUTO_INCREMENT PRIMARY KEY, -- In PostgreSQL use: professor_id SERIAL PRIMARY KEY
    prof_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    department_id INT,
    salary DECIMAL(10,2),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);


-- =============================================================================
-- Task 2: Verify Normalisation
-- =============================================================================
/*
1NF (First Normal Form) Compliance:
----------------------------------
- Requirement: All columns must contain only atomic (indivisible) values, and there must be no repeating groups.
- Compliance: Yes. For example, first_name and last_name are separated; email is single-valued. 
  A violation would occur if a "phone_numbers" field stored multiple comma-separated values 
  (e.g., '123-456, 789-012') in a single cell. Instead, we should create a separate table for multiple phone numbers.

2NF (Second Normal Form) Compliance:
-----------------------------------
- Requirement: Must be in 1NF, and all non-key columns must be fully functionally dependent on the entire primary key.
- Compliance: Yes. In the enrollments table, the primary key is 'enrollment_id'. Non-key attributes like 'grade' 
  and 'enrollment_date' depend fully on this ID. 
  Even if we consider a composite candidate key of (student_id + course_id), the non-key attribute 'grade' 
  depends on both the student and the course together. There are no partial dependencies (where a non-key column 
  depends only on a part of a composite key).

3NF (Third Normal Form) Compliance:
----------------------------------
- Requirement: Must be in 2NF, and there must be no transitive dependencies (non-key columns depending on other non-key columns).
- Compliance: Yes. All non-key attributes depend directly and only on the primary keys.
  For example, in the students table, 'department_id' depends on 'student_id', and the details of that department 
  are stored in the departments table. Storing 'dept_name' directly inside the students table would violate 3NF 
  because 'dept_name' would depend on 'department_id', which in turn depends on 'student_id' (a transitive dependency).
*/


-- =============================================================================
-- Task 3: Alter and Extend the Schema
-- =============================================================================

-- 10. Add phone_number column to students table
ALTER TABLE students ADD COLUMN phone_number VARCHAR(15);

-- 11. Add max_seats column to courses table
ALTER TABLE courses ADD COLUMN max_seats INT DEFAULT 60;

-- 12. Add a CHECK constraint to enrollments grade (must be one of 'A','B','C','D','F' or NULL)
ALTER TABLE enrollments ADD CONSTRAINT chk_grade CHECK (grade IN ('A','B','C','D','F') OR grade IS NULL);

-- 13. Rename hod_name in departments to head_of_dept
-- In MySQL:
-- ALTER TABLE departments CHANGE COLUMN hod_name head_of_dept VARCHAR(100);
-- In PostgreSQL / ANSI SQL standard:
ALTER TABLE departments RENAME COLUMN hod_name TO head_of_dept;

-- 14. Drop the phone_number column (simulate rollback)
ALTER TABLE students DROP COLUMN phone_number;
