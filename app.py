"""
Main Flask application for Buddy.Fi backend.

Application setup section.
Initializes Flask app instance, enables CORS for frontend communication,
configures bcrypt for password hashing, loads environment variables,
sets up database connection, and prepares the DataManager.

Provides routes for:
- public access
- JWT-protected routes
- login/authentication
- retrieving current user data (via JWT)
- fetching course data
"""

from flask import Flask, request, jsonify, make_response, render_template, session
from datetime import datetime, timedelta
from functools import wraps
from flask_bcrypt import Bcrypt
from data_manager import DataManager
from extentions import db
from flask_cors import CORS
from dotenv import load_dotenv
import os
import jwt

# App initialization
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])
bcrypt = Bcrypt(app)  # initiates bcrypt für hashing password

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/budifi.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

load_dotenv()
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

db.init_app(app)  # Links the database and the App

data_manager = DataManager(db)  # Creates an object of your DataManager Class


def token_required(func):
    """
    Decorator to protect routes with JWT authentication.

    Expects a JWT token passed as a query parameter.
    Decodes and validates the token before allowing access
    to the wrapped route function.
    """

    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert': 'Token is missing'})
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithm='HS256')
            # current_user = payload['user']
            # TODO: später unten das anpassen: return func(current_user, *args, **kwargs)
            # TODO: später unten das anpassen:
            # @token_required
            # def get_progress(current_user):
            #     return f"Progress for user: {current_user}"
        except jwt.ExpiredSignatureError:
            return jsonify({'Alert!': 'Token expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'Alert!': 'Invalid token'}), 403

        return func(*args, **kwargs)

    return decorated


# Home
@app.route('/')
def home():
    """Root home route – returns login page or login status."""
    if not session.get('logged_in'):
        return render_template('login.html'), 200
    else:
        return jsonify('Logged in currently!'), 200


# Public Area
@app.route('/public')
def public():
    """Public route – accessible without authentication."""
    return 'For Public'


# Protected Area → Authenticated
@app.route('/auth')
@token_required
def auth():
    """Protected route – requires JWT token to access."""
    return 'JWT is verified. Welcome to your dashboard!'


# Login
@app.route('/login', methods=['POST'])
def login():
    """Login route – verifies credentials and returns JWT token."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload received"}), 400
    email = data.get('email')
    password = data.get('password')
    if email and password == '123':
        session['logged_in'] = True
        token = jwt.encode({
            'user': email,
            'expiration': str(datetime.utcnow() + timedelta(seconds=120))
        },
            app.config['SECRET_KEY'],
            algorithm='HS256')
        return jsonify({'token': token})
    else:
        return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm:"Authentication Failed!"'})


# Logged in User
@app.route('/me', methods=['GET'])
def me():
    """
    Returns current logged-in user details from JWT token.

    Parses Bearer token from Authorization header, decodes it,
    validates expiration, and fetches user from database.
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        email = payload.get("user")
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 403
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email
    }), 200


@app.route('/api/courses')
def get_courses():
    """Fetch all available courses from the database."""
    courses = data_manager.list_courses()
    print(courses)
    # hier müssen alle Kursdaten rein und die komme aus Datamanager z.
    return jsonify(courses), 200


# @app.route('/api/signup', methods=['POST'])
# def add_user():
#     """Adds a new user to the database from form input."""
#     data = request.get_json()
#     first_name = data.get('first_name')
#     last_name = data.get('last_name')
#     email = data.get('email')
#     password = data.get('password')
#     hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
#     new_user = User(
#         first_name=first_name,
#         last_name=last_name,
#         email=email,
#         password=hashed_password)
#
#     data_manager.create_user(new_user)
#
#     return jsonify({"message": "user created successfully"}), 200


# @app.route('/api/user/<int:user_id>/dashboard', methods=['GET'])
# def show_user_dashboard(user_id):
#   """Shows dashboard including user progress."""
#   user_dashboard_data = data_manager.get_current_user_dashboard(user_id)
#   print(user_dashboard_data)
#   return jsonify(user_dashboard_data), 200


if __name__ == '__main__':
    with app.app_context():
        from models.user import User
        from models.lesson import Lesson
        from models.question import Question
        from models.quiz import Quiz
        from models.course import Course
        from models.enrollment import Enrollment

        db.create_all()

    app.run(host="0.0.0.0", port=5003, debug=True)
