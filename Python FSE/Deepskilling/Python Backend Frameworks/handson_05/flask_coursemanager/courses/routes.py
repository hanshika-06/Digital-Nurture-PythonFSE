from flask import Blueprint, jsonify, request
from extensions import db
from courses.models import Course,Student,Enrollment

courses_bp = Blueprint(
    "courses",
    __name__,
    url_prefix="/api/courses"
)

@courses_bp.route("/", methods=["GET"])
def get_courses():

    courses = Course.query.all()

    return jsonify(
        [course.to_dict() for course in courses]
    )
@courses_bp.route("/", methods=["POST"])
def create_course():

    data = request.get_json()

    course = Course(
        name=data["name"],
        code=data["code"],
        credits=data["credits"],
        department_id=data["department_id"]
    )

    db.session.add(course)

    db.session.commit()

    return jsonify(course.to_dict()),201
@courses_bp.route("/<int:course_id>", methods=["GET"])
def get_course(course_id):

    course = Course.query.get_or_404(course_id)

    return jsonify(course.to_dict())

@courses_bp.route("/<int:course_id>/students/",methods=["GET"])
def course_students(course_id):

    students=Student.query.join(
        Enrollment
    ).filter(
        Enrollment.course_id==course_id
    ).all()

    return jsonify(
        [student.to_dict() for student in students]
    )

@courses_bp.route("/<int:course_id>",methods=["PUT"])
def update_course(course_id):

    course = Course.query.get_or_404(course_id)

    data=request.get_json()

    course.name=data.get("name",course.name)

    course.code=data.get("code",course.code)

    course.credits=data.get("credits",course.credits)

    db.session.commit()

    return jsonify(course.to_dict())

@courses_bp.route("/<int:course_id>",methods=["DELETE"])
def delete_course(course_id):

    course=Course.query.get_or_404(course_id)

    db.session.delete(course)

    db.session.commit()

    return jsonify({
        "message":"Course deleted"
    })