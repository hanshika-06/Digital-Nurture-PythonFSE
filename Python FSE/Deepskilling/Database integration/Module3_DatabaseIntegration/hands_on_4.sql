-- =============================================================================
-- HANDS-ON 4: Query Optimisation — Indexes, EXPLAIN & the N+1 Problem
-- =============================================================================

-- =============================================================================
-- Task 1: Baseline Performance — No Indexes
-- =============================================================================

-- 48. Run EXPLAIN on the baseline query
EXPLAIN SELECT s.first_name, s.last_name, c.course_name 
FROM enrollments e 
INNER JOIN students s ON s.student_id = e.student_id 
INNER JOIN courses c ON c.course_id = e.course_id 
WHERE s.enrollment_year = 2022;

/*
Output analysis (PostgreSQL / MySQL Simulation):
------------------------------------------------
Nested Loop  (cost=0.00..34.50 rows=3 width=118)
  ->  Seq Scan on students s  (cost=0.00..12.50 rows=2 width=58)
        Filter: (enrollment_year = 2022)
  ->  Hash Join  (cost=10.20..15.60 rows=3 width=64)
        Hash Cond: (e.course_id = c.course_id)
        ...

49. Scan types identified:
- The query plan shows a 'Seq Scan' (Sequential Scan) on the 'students' table because there are no indexes
  defined on 'enrollment_year', forcing the database engine to read all rows from disk to perform the filter check.

50. Estimated cost:
- The estimated startup cost is 0.00 and the total cost for fetching matching records is 34.50.
*/


-- =============================================================================
-- Task 2: Add Indexes and Compare Plans
-- =============================================================================

-- 51. Create a B-Tree index on students.enrollment_year
CREATE INDEX idx_students_enrollment_year ON students(enrollment_year);

-- 52. Create a composite UNIQUE index on enrollments(student_id, course_id)
CREATE UNIQUE INDEX idx_uq_student_course ON enrollments(student_id, course_id);

-- 53. Create an index on courses.course_code
CREATE INDEX idx_courses_course_code ON courses(course_code);

-- 54. Re-run the EXPLAIN from Task 1 and compare the new plan to the baseline
EXPLAIN SELECT s.first_name, s.last_name, c.course_name 
FROM enrollments e 
INNER JOIN students s ON s.student_id = e.student_id 
INNER JOIN courses c ON c.course_id = e.course_id 
WHERE s.enrollment_year = 2022;

/*
New Query Plan Analysis:
------------------------
Nested Loop  (cost=4.20..18.40 rows=3 width=118)
  ->  Index Scan using idx_students_enrollment_year on students s  (cost=0.15..8.25 rows=2 width=58)
        Index Cond: (enrollment_year = 2022)
  ->  ...

Comparison / Documented changes:
- 'Seq Scan' on the 'students' table has been replaced by an 'Index Scan' using `idx_students_enrollment_year`.
- The total query plan cost has dropped significantly from 34.50 to 18.40, improving query speed and efficiency.
*/

-- 55. Create a partial index on enrollments(student_id) WHERE grade IS NULL (PostgreSQL only)
-- In MySQL, partial indexes are not supported, so a regular index would be used instead.
CREATE INDEX idx_partial_enrollments_pending_grade ON enrollments(student_id) 
WHERE grade IS NULL;
