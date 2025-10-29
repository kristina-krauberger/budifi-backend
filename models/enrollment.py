"""Many-to-Many-Beziehung mit Zusatzinformationen - Sie verbindet User und Course Tabelle"""

from extentions import db
from datetime import datetime

class Enrollment(db.Model):
    """Database for enrollment & progress model."""
    __tablename__ = "enrollment"

    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    course_id = db.Column(db.Integer, db.ForeignKey("course.course_id"))
    progress = db.Column(db.Integer, nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(32), nullable=False)