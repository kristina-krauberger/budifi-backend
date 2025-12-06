from enum import nonmember

from sqlalchemy import select
from models.course import Course
from models.user import User
from models.enrollment import Enrollment
from datetime import datetime
from flask_bcrypt import Bcrypt


class DataManager:

    def __init__(self, app, db):
        """Initializes the DataManager with a database session."""
        self.app = app
        self.db = db
        self.bcrypt = Bcrypt(app)  # initiates bcrypt für hashing password


    def create_user(self, user: User):
        """Creates a new user with the given user data. Returns error message if input is invalid."""

        user.password = self.hash_value(user.password)

        try:
            self.db.session.add(user)
            self.db.session.commit()
            return None
        except Exception as e:          #TODO: später "Exception" entfernen
            return f"{e}"


    def hash_value(self, string):
        return self.bcrypt.generate_password_hash(string).decode("utf-8")


    def get_user_with_email_password(self, email, password):
        hash_password = self.hash_value(password)
        user = self.db.session.execute(select(User).where(User.email==email, User.password==hash_password)).scalar_one_or_none()
        if not user:
            return None
        return user


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

