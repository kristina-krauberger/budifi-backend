from sqlalchemy import select
from models.course import Course
from datetime import datetime

#TODO LÖSCHEN?

class CourseDataManager:

    def __init__(self, db):
        """Initializes the DataManager with a database session."""
        self.db = db

    def create_course(self):

        try:
            self.db.session.add(user)
            self.db.session.commit()
            return None
        except Exception as e:          #TODO: später "Exception" entfernen
            return f"{e}"


    def get_all_courses(self):

        courses = self.db.session.execute(select(Course)).scalars().all()
        return courses


    def get_one_course(self):
        pass


    def delete_course(self):
        pass


    def update_course(self):
        pass


