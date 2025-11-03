from models.course import Course
from models.user import User
from models.enrollment import Enrollment

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


