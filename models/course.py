from extentions import db

class Course(db.Model):
    """Database for course model"""
    __tablename__ = "course"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(32), nullable=False)
