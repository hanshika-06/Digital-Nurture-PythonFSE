-- =============================================================================
-- HANDS-ON 3: Advanced SQL — Subqueries, Views & Transactions
-- =============================================================================

-- =============================================================================
-- Task 1: Subqueries
-- =============================================================================

-- 35. Find all students enrolled in more courses than the average number of enrollments per student
SELECT s.student_id, CONCAT(s.first_name, ' ', s.last_name) AS student_name
FROM students s
INNER JOIN enrollments e ON s.student_id = e.student_id
GROUP BY s.student_id
HAVING COUNT(e.enrollment_id) > (
    SELECT AVG(enrollment_count) 
    FROM (
        SELECT COUNT(enrollment_id) AS enrollment_count 
        FROM enrollments 
        GROUP BY student_id
    ) AS sub
);

-- 36. List courses in which all enrolled students have received a grade of 'A'
SELECT c.course_id, c.course_name
FROM courses c
WHERE NOT EXISTS (
    SELECT 1 FROM enrollments e 
    WHERE e.course_id = c.course_id AND (e.grade != 'A' OR e.grade IS NULL)
) AND EXISTS (
    SELECT 1 FROM enrollments e WHERE e.course_id = c.course_id
);

-- 37. Find the professor with the highest salary in each department using a correlated subquery
SELECT p1.professor_id, p1.prof_name, p1.department_id, p1.salary
FROM professors p1
WHERE p1.salary = (
    SELECT MAX(p2.salary) 
    FROM professors p2 
    WHERE p2.department_id = p1.department_id
);

-- 38. Using a subquery in the FROM clause (derived table), calculate the per-department average salary 
-- and then filter to departments where that average exceeds 85,000
SELECT dept.dept_name, dept_avg.avg_salary
FROM departments dept
INNER JOIN (
    SELECT department_id, AVG(salary) AS avg_salary
    FROM professors
    GROUP BY department_id
) AS dept_avg ON dept.department_id = dept_avg.department_id
WHERE dept_avg.avg_salary > 85000.00;


-- =============================================================================
-- Task 2: Creating and Using Views
-- =============================================================================

-- 39. Create view vw_student_enrollment_summary
-- Calculates GPA based on: A=4, B=3, C=2, D=1, F=0
CREATE OR REPLACE VIEW vw_student_enrollment_summary AS
SELECT 
    s.student_id,
    CONCAT(s.first_name, ' ', s.last_name) AS full_name,
    d.dept_name AS department,
    COUNT(e.enrollment_id) AS courses_enrolled,
    ROUND(AVG(
        CASE e.grade
            WHEN 'A' THEN 4
            WHEN 'B' THEN 3
            WHEN 'C' THEN 2
            WHEN 'D' THEN 1
            WHEN 'F' THEN 0
            ELSE NULL
        END
    ), 2) AS gpa
FROM students s
INNER JOIN departments d ON s.department_id = d.department_id
LEFT JOIN enrollments e ON s.student_id = e.student_id
GROUP BY s.student_id, s.first_name, s.last_name, d.dept_name;

-- 40. Create view vw_course_stats showing course_name, course_code, total_enrollments, and avg_gpa
CREATE OR REPLACE VIEW vw_course_stats AS
SELECT 
    c.course_name,
    c.course_code,
    COUNT(e.enrollment_id) AS total_enrollments,
    ROUND(AVG(
        CASE e.grade
            WHEN 'A' THEN 4
            WHEN 'B' THEN 3
            WHEN 'C' THEN 2
            WHEN 'D' THEN 1
            WHEN 'F' THEN 0
            ELSE NULL
        END
    ), 2) AS avg_gpa
FROM courses c
LEFT JOIN enrollments e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_name, c.course_code;

-- 41. Query vw_student_enrollment_summary to find students with GPA above 3.0
SELECT * FROM vw_student_enrollment_summary 
WHERE gpa > 3.00;

-- 42. Attempt to UPDATE a row through vw_student_enrollment_summary and explain behavior
-- UPDATE vw_student_enrollment_summary SET gpa = 3.8 WHERE student_id = 1;
/*
Explanation:
Multi-table views (views built using joins, aggregations, or group by clauses) are NOT updatable in relational databases. 
This is because the database cannot unambiguously translate a modification to the view's computed columns (like `gpa` or `courses_enrolled`)
into corresponding write operations on the underlying base tables (like modifying a single row's grade in `enrollments`).
*/

-- 43. DROP both views and recreate vw_student_enrollment_summary as single-table subset view WITH CHECK OPTION
DROP VIEW vw_student_enrollment_summary;
DROP VIEW vw_course_stats;

-- Create single-table subset view of students enrolled in department 1 with check option
CREATE VIEW vw_student_dept1_subset AS
SELECT student_id, first_name, last_name, email, department_id, enrollment_year
FROM students
WHERE department_id = 1
WITH CHECK OPTION;


-- =============================================================================
-- Task 3: Stored Procedures and Transactions (PostgreSQL PL/pgSQL Standard)
-- =============================================================================

-- 44. Function fn_enroll_student (PostgreSQL)
-- Accepts student_id, course_id, and enrollment_date. Checks for duplicate enrollment, and inserts.
/*
CREATE OR REPLACE FUNCTION fn_enroll_student(
    p_student_id INT,
    p_course_id INT,
    p_enrollment_date DATE
) RETURNS VOID AS $$
BEGIN
    -- Check for duplicate
    IF EXISTS (
        SELECT 1 FROM enrollments 
        WHERE student_id = p_student_id AND course_id = p_course_id
    ) THEN
        RAISE EXCEPTION 'Student is already enrolled in this course.';
    END IF;

    -- Insert record
    INSERT INTO enrollments (student_id, course_id, enrollment_date)
    VALUES (p_student_id, p_course_id, p_enrollment_date);
END;
$$ LANGUAGE plpgsql;
*/

-- Setup Department Transfer Log table
CREATE TABLE department_transfer_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY, -- In PostgreSQL use: log_id SERIAL PRIMARY KEY
    student_id INT,
    old_department_id INT,
    new_department_id INT,
    transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 45. Procedure sp_transfer_student (PostgreSQL)
-- Moves a student from one department to another. Wraps UPDATE and log-insert inside a single transaction.
/*
CREATE OR REPLACE PROCEDURE sp_transfer_student(
    p_student_id INT,
    p_new_dept_id INT
) AS $$
DECLARE
    v_old_dept_id INT;
BEGIN
    -- Get current department
    SELECT department_id INTO v_old_dept_id FROM students WHERE student_id = p_student_id;
    
    IF v_old_dept_id IS NULL THEN
        RAISE EXCEPTION 'Student does not exist.';
    END IF;
    
    -- Verify new department exists
    IF NOT EXISTS (SELECT 1 FROM departments WHERE department_id = p_new_dept_id) THEN
        RAISE EXCEPTION 'Target department does not exist.';
    END IF;

    -- Perform updates
    UPDATE students 
    SET department_id = p_new_dept_id 
    WHERE student_id = p_student_id;

    INSERT INTO department_transfer_log (student_id, old_department_id, new_department_id)
    VALUES (p_student_id, v_old_dept_id, p_new_dept_id);
    
    -- Commit is handled automatically at scope end or can be called explicitly
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;
$$ LANGUAGE plpgsql;
*/

-- 46. Test rollback example SQL
-- START TRANSACTION;
-- CALL sp_transfer_student(1, 999); -- Invalid dept id triggers exception and triggers rollback

-- 47. Use SAVEPOINT example SQL
/*
START TRANSACTION;
INSERT INTO enrollments (student_id, course_id, enrollment_date, grade) 
VALUES (1, 4, '2026-07-02', 'A');

SAVEPOINT after_first_enrollment;

-- Deliberately fail the second (violates unique or foreign key constraint)
INSERT INTO enrollments (student_id, course_id, enrollment_date, grade) 
VALUES (999, 1, '2026-07-02', 'B'); -- Fails due to invalid student_id FK

-- Rollback to savepoint on error
ROLLBACK TO SAVEPOINT after_first_enrollment;
COMMIT;
*/
