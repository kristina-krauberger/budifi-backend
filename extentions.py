"""
Application extensions module.

Creates and exposes reusable extension instances
such as SQLAlchemy (database) and Bcrypt (password hashing).
These are initialized with the Flask app inside app.py.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()  # initiates bcrypt für hashing password
