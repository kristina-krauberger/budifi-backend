from extentions import db

class User(db.Model):
    """Database model for user"""
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=True)
    email = db.Column(db.String(32), nullable=False, unique=True)  #unique kein zweiter user kann sich damit anmelden
    password = db.Column(db.String(32), nullable=False)








