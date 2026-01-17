from sqlalchemy import select
from models.course import Course
from models.user import User
from models.enrollment import Enrollment
from datetime import datetime
from service.data_manager.course_data_manager import CourseDataManager

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


    def get_current_user_dashboard(self, user_id):
        """Fetches all user-related dashboard data, including personal info, enrolled courses, and progress."""

        # Fetches personal data of current user for greeting and identification in dashboard.
        user = self.db.session.execute(select(User).where(User.id==user_id)).scalar_one()
        first_name = user.first_name

        # Fetches enrollment data, including courses, progress and enrollment date for the current user.
        enrollment = self.db.session.execute(select(Enrollment).filter_by(user_id=user_id)).scalars().all()

        # Calculates how many days have passed since the current user first enrolled.
        enrolled_at = enrollment[0].enrolled_at
        days_since_enrolled = (datetime.utcnow() - enrolled_at).days

        # Builds a list of all courses with their progress data for current user.
        courses_data = []
        for entry in enrollment:
            course = self.db.session.execute(select(Course).where(Course.id==entry.course_id)).scalar_one()
            progress = entry.progress
            courses_data.append({
                "course_id": course.id,
                "course_name": course.course_name,
                "progress": progress
            })

        # Collects all relevant data of current user for display to the dashboard in a dictionary.
        user_dashboard_data = {
            "user_id": user.id,
            "first_name": first_name,
            "days_since_enrolled": days_since_enrolled,
            "courses": courses_data
        }
        return user_dashboard_data


    def list_courses(self):

        courses = self.db.session.query(Course).all()
        courses_data = []

        for course in courses:
            course_data = {
                "id": course.id,
                "course_number": course.course_number,
                "title": course.course_title,
                "isLastCourse": course.is_last_course,
                "lessons": []
            }

            for lesson in sorted(course.lessons, key=lambda l: l.lesson_number):
                lesson_data = {
                    "id": lesson.id,
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