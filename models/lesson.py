from extentions import db

class Lesson(db.Model):
    __tablename__ = 'lesson'

    id = db.Column(db.Integer, primary_key=True)
    lesson_number = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))
    title = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer)
    is_last_lesson = db.Column(db.Boolean, default=False)
    summary_congrats = db.Column(db.Text, nullable=False)
    summary_text = db.Column(db.Text, nullable=False)

    # Each lesson has one quiz (1:1 relationship)
    quiz = db.relationship("Quiz", backref="lesson", uselist=False)
    lesson_progress = db.relationship("LessonProgress", backref="lesson", uselist=False)

    def __repr__(self):
        return f"<Lesson {self.title}>"