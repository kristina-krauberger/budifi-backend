from extentions import db

class Course(db.Model):
    """Database for course model"""
    __tablename__ = "course"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_number = db.Column(db.Integer, nullable=False)
    course_title = db.Column(db.String(32), nullable=False)
    is_last_course = db.Column(db.Boolean, nullable=False)


    # List of lessons, enrollments and progresses linked to this course (not a direct DB column, but relationship)
    lessons = db.relationship("Lesson", backref="course", lazy=True)
