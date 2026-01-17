from extentions import db

class Quiz(db.Model):
    __tablename__ = 'quiz'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_number = db.Column(db.Integer, nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lesson.id"))

    # One-to-many relationship: A quiz can have multiple questions
    questions = db.relationship("Question", backref="quiz", lazy=True)