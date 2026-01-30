"""Many-to-Many-Beziehung mit Zusatzinformationen - Sie verbindet User und Course Tabelle"""
from email.policy import default

from extentions import db
from datetime import datetime

class LessonProgress(db.Model):
    """Database for enrollment & progress model."""
    __tablename__ = "lesson_progress"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    lesson_id = db.Column(db.Integer, db.ForeignKey("lesson.id"))
    is_completed = db.Column(db.Integer, nullable=False, default=0)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)




