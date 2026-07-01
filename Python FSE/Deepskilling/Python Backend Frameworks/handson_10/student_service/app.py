import os
import requests
from flask import Flask, request, jsonify, abort
# pyrefly: ignore [missing-import]
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Database setup - students.db is inside the student_service directory
db_path = os.path.join(os.path.dirname(__file__), "students.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

COURSE_SERVICE_URL = os.environ.get("COURSE_SERVICE_URL", "http://localhost:5001")

# Models
class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    enrollment_year = db.Column(db.Integer, nullable=False)

    enrollments = db.relationship("Enrollment", backref="student", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "enrollment_year": self.enrollment_year
        }

class Enrollment(db.Model):
    __tablename__ = "enrollments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    course_id = db.Column(db.Integer, nullable=False)  # Not a DB Foreign Key as they are separate databases
    grade = db.Column(db.String(2))

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "grade": self.grade
        }

# Initialize Database
with app.app_context():
    db.create_all()

# Routes
@app.route("/api/students/", methods=["GET", "POST"])
def manage_students():
    if request.method == "POST":
        data = request.get_json() or {}
        required = ["first_name", "last_name", "email", "enrollment_year"]
        if not all(k in data for k in required):
            return jsonify({"error": f"Missing required fields: {required}"}), 400

        # Unique email validation
        existing = Student.query.filter_by(email=data["email"]).first()
        if existing:
            return jsonify({"error": f"Student with email '{data['email']}' already exists"}), 400

        student = Student(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            enrollment_year=data["enrollment_year"]
        )
        db.session.add(student)
        db.session.commit()
        return jsonify(student.to_dict()), 201
    else:
        students = Student.query.all()
        return jsonify([s.to_dict() for s in students])

@app.route("/api/students/<int:id>/", methods=["GET", "PUT", "DELETE"])
def student_detail(id):
    student = Student.query.get_or_404(id)
    if request.method == "GET":
        return jsonify(student.to_dict())
    elif request.method == "PUT":
        data = request.get_json() or {}
        student.first_name = data.get("first_name", student.first_name)
        student.last_name = data.get("last_name", student.last_name)
        if "email" in data and data["email"] != student.email:
            existing = Student.query.filter_by(email=data["email"]).first()
            if existing:
                return jsonify({"error": f"Student with email '{data['email']}' already exists"}), 400
            student.email = data["email"]
        student.enrollment_year = data.get("enrollment_year", student.enrollment_year)
        db.session.commit()
        return jsonify(student.to_dict())
    elif request.method == "DELETE":
        db.session.delete(student)
        db.session.commit()
        return "", 204

@app.route("/api/students/<int:student_id>/enroll", methods=["POST"])
def enroll_student(student_id):
    # Verify student exists
    student = Student.query.get_or_404(student_id)
    
    data = request.get_json() or {}
    if "course_id" not in data:
        return jsonify({"error": "course_id is required"}), 400
        
    course_id = data["course_id"]
    grade = data.get("grade")

    # Check if duplicate enrollment in Student database
    existing_enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing_enrollment:
        return jsonify({"error": "Student is already enrolled in this course"}), 400

    # Call Course Service GET /api/courses/{course_id}/ to verify course exists
    try:
        url = f"{COURSE_SERVICE_URL}/api/courses/{course_id}/"
        response = requests.get(url, timeout=5)
        if response.status_code == 404:
            return jsonify({"error": f"Course with id {course_id} does not exist in Course Service"}), 404
        elif response.status_code != 200:
            return jsonify({"error": "Failed to verify course with Course Service"}), 500
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Course Service is unavailable (Connection Error)"}), 503
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"An error occurred while contacting Course Service: {str(e)}"}), 500

    # Create enrollment
    enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id,
        grade=grade
    )
    db.session.add(enrollment)
    db.session.commit()
    
    # Simulate background task
    print(f"Simulating confirmation email to {student.email} for course {course_id}")
    
    return jsonify(enrollment.to_dict()), 201

# Endpoint to view enrollments for testing
@app.route("/api/students/enrollments/", methods=["GET"])
def get_all_enrollments():
    enrollments = Enrollment.query.all()
    return jsonify([e.to_dict() for e in enrollments])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
