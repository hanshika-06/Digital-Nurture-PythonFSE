import os
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Database setup - courses.db is inside the course_service directory
db_path = os.path.join(os.path.dirname(__file__), "courses.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Models
class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    head_of_dept = db.Column(db.String(100))
    budget = db.Column(db.Float)

    courses = db.relationship("Course", backref="department", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "head_of_dept": self.head_of_dept,
            "budget": self.budget
        }

class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "credits": self.credits,
            "department_id": self.department_id
        }

# Initialize Database
with app.app_context():
    db.create_all()

# Routes
@app.route("/api/departments/", methods=["GET", "POST"])
def manage_departments():
    if request.method == "POST":
        data = request.get_json() or {}
        if "name" not in data:
            return jsonify({"error": "name is required"}), 400
        dept = Department(
            name=data["name"],
            head_of_dept=data.get("head_of_dept"),
            budget=data.get("budget")
        )
        db.session.add(dept)
        db.session.commit()
        return jsonify(dept.to_dict()), 201
    else:
        depts = Department.query.all()
        return jsonify([d.to_dict() for d in depts])

@app.route("/api/departments/<int:id>/", methods=["GET"])
def get_department(id):
    dept = Department.query.get_or_404(id)
    return jsonify(dept.to_dict())

@app.route("/api/courses/", methods=["GET", "POST"])
def manage_courses():
    if request.method == "POST":
        data = request.get_json() or {}
        required = ["name", "code", "credits", "department_id"]
        if not all(k in data for k in required):
            return jsonify({"error": f"Missing required fields: {required}"}), 400
            
        # Verify department exists
        dept = Department.query.get(data["department_id"])
        if not dept:
            return jsonify({"error": f"Department {data['department_id']} not found"}), 400

        # Check code unique constraint
        existing = Course.query.filter_by(code=data["code"]).first()
        if existing:
            return jsonify({"error": f"Course code '{data['code']}' already exists"}), 400

        course = Course(
            name=data["name"],
            code=data["code"],
            credits=data["credits"],
            department_id=data["department_id"]
        )
        db.session.add(course)
        db.session.commit()
        return jsonify(course.to_dict()), 201
    else:
        courses = Course.query.all()
        return jsonify([c.to_dict() for c in courses])

@app.route("/api/courses/<int:id>/", methods=["GET", "PUT", "DELETE"])
def course_detail(id):
    course = Course.query.get_or_404(id)
    if request.method == "GET":
        return jsonify(course.to_dict())
    elif request.method == "PUT":
        data = request.get_json() or {}
        course.name = data.get("name", course.name)
        course.code = data.get("code", course.code)
        course.credits = data.get("credits", course.credits)
        if "department_id" in data:
            dept = Department.query.get(data["department_id"])
            if not dept:
                return jsonify({"error": "Department not found"}), 400
            course.department_id = data["department_id"]
        db.session.commit()
        return jsonify(course.to_dict())
    elif request.method == "DELETE":
        db.session.delete(course)
        db.session.commit()
        return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
