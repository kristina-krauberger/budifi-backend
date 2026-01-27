from models.course import Course
from models.user import User
from models.lesson_progress import LessonProgress
from models.lesson import Lesson


class DataManager:

    def __init__(self, db):
        """Initializes the DataManager with a database session."""
        self.db = db


    def create_user(self, user: User):
        """Creates a new user with the given user data. Returns error message if input is invalid."""

        try:
            self.db.session.add(user)
            self.db.session.commit()
            return None
        except Exception as e:          #TODO: später "Exception" entfernen
            return f"{e}"


    def list_courses(self):

        courses = self.db.session.query(Course).all()
        courses_data = []

        for course in courses:
            course_data = {
                "course_id": course.id,
                "course_number": course.course_number,
                "title": course.course_title,
                "isLastCourse": course.is_last_course,
                "lessons": []
            }

            for lesson in sorted(course.lessons, key=lambda l: l.lesson_number):
                lesson_data = {
                    "lesson_id": lesson.id,
                    "lesson_number": lesson.lesson_number,
                    "title": lesson.title,
                    "duration": lesson.duration,
                    "isCompleted": lesson.is_completed,
                    "isLastLesson": lesson.is_last_lesson,
                    "summaryCongrats": lesson.summary_congrats,
                    "summaryText": lesson.summary_text,
                    "quiz": []
                }

                if lesson.quiz:
                    questions_data = []
                    for question in sorted(lesson.quiz.questions, key=lambda q: q.question_number):
                        questions_data.append({
                            "quiz_number": question.quiz.quiz_number,
                            "question_number": question.question_number,
                            "question_text": question.question_text,
                            "optionsAnswer": [question.option_1, question.option_2, question.option_3],
                            "correctAnswer": question.correct_option
                        })
                    lesson_data["quiz"] = questions_data

                course_data["lessons"].append(lesson_data)

            courses_data.append(course_data)

        return {"courses": courses_data}


    def list_lesson_progress(self, user_id):

        lesson_progress = self.db.session.query(
            Lesson.course_id,
            Lesson.id,
            LessonProgress.is_completed
        ).outerjoin(
            LessonProgress,
            (Lesson.id == LessonProgress.lesson_id) & (LessonProgress.user_id == user_id)
        ).all()

        print(lesson_progress)

        courses_progress = []

        for course_id, lesson_id, is_completed in lesson_progress:
            course_entry = next((c for c in courses_progress if c["course_id"] == course_id), None)

            if not course_entry:
                course_entry = {
                    "course_id": course_id,
                    "completed_lessons": 0,
                    "completed_percentage": 0,
                    "lessons": []
                }
                courses_progress.append(course_entry)

            course_entry["lessons"].append({
                "lesson_id": lesson_id,
                "is_completed": bool(is_completed)
            })
            if is_completed:
                course_entry["completed_lessons"] += 1

            for course in courses_progress:
                total = len(course["lessons"])
                completed = course["completed_lessons"]
                course["completed_percentage"] = int((completed / total) * 100) if total > 0 else 0

        return {"courses": courses_progress}