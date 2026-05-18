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

from flask import Flask, request, jsonify, make_response, session
from datetime import datetime, timedelta
from functools import wraps
from data_manager import DataManager
from models import User
from extentions import db, bcrypt
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import os
import jwt

# Initialize Flask app and allow CORS for local (localhost) and deployed (vercel.app) frontend
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "https://buddyfi-2.vercel.app", "http://localhost:5174",
                   "http://127.0.0.1:5173"])

load_dotenv()  # Load environment variables from the .env file

# Set database path using absolute project path (safe for deployment)
database_url = os.environ.get("DATABASE_URL")

# If using a relative SQLite path, convert it to an absolute path
if database_url.startswith("sqlite:///data"):
    basedir = os.path.abspath(os.path.dirname(__file__))
    database_url = f"sqlite:///{os.path.join(basedir, 'data/budifi.db')}"

# Apply the final database URL to the Flask app config
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")  # Used for JWT encoding/decoding

db.init_app(app)  # Links the database and the App
bcrypt.init_app(app)

data_manager = DataManager(db)  # Creates an object of your DataManager Class

OPENAI_API_KEY = os.getenv("SECRET_KEY_OPENAI")
client = OpenAI(api_key=OPENAI_API_KEY)  # Creates OpenAI Client


def token_required(func):
    """
    Decorator to protect routes with JWT authentication.

    Expects a JWT token passed as a query parameter.
    Decodes and validates the token before allowing access
    to the wrapped route function.
    """

    @wraps(func)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token is missing"}), 401

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return func(*args, **kwargs)

    return decorated

@app.route('/api/health', methods=['GET'])
def health_track():
    return {"status": "ok"}


# Login
@app.route('/api/login', methods=['POST'])
def login():
    """Login route – verifies credentials and returns JWT token."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload received"}), 400
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    password = data.get('password')
    if user and bcrypt.check_password_hash(user.password, password):
        session['logged_in'] = True
        token = jwt.encode({
            'user_id': user.id,
            'user': email,
            'expiration': str(datetime.utcnow() + timedelta(seconds=120))
        },
            app.config['SECRET_KEY'],
            algorithm='HS256')
        return jsonify({'token': token})
    else:
        return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm:"Authentication Failed!"'})


# Logged in User
@app.route('/api/me', methods=['GET'])
def me():
    """
    Returns current logged-in user details from JWT token.

    Parses Bearer token from Authorization header, decodes it,
    validates expiration, and fetches user from database.
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "You must be logged in to access this resource."}), 401

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        email = payload.get("user")
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Your session has expired. Please log in again."}), 403
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token. Authentication failed."}), 403
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email
    }), 200


@app.route('/api/courses', methods=['GET'])
@token_required
def get_courses():
    """Fetch all available courses from the database."""
    courses = data_manager.get_courses()
    return jsonify(courses), 200


@app.route('/api/user/<int:user_id>/progress', methods=['GET'])
@token_required
def get_progress_for_user(user_id):
    """Fetch progress for user from the database."""
    progress = data_manager.get_lesson_progress(user_id)
    return jsonify(progress)


@app.route('/api/user/<int:user_id>/progress', methods=['PUT'])
@token_required
def update_progress_for_user(user_id):
    """
    Updates lesson progress for a specific user.
    Expects JSON payload containing lesson_id and is_completed flag.
    Writes updated progress state (is_completed) to the database.
    """
    data = request.get_json()
    lesson_id = data.get('lesson_id', 'N/A')
    is_completed = data.get('is_completed', 'false')
    data_manager.update_lesson_progress(user_id, lesson_id, is_completed)

    return jsonify({
        "user_id": user_id,
        "lesson_id": lesson_id,
        "is_completed": is_completed
    }), 200


@app.route('/api/register', methods=['POST'])
def create_user():
    """Adds a new user to the database from form input."""
    data = request.get_json()
    print("📩 REGISTER HIT")
    print(data)
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    existing_user = data_manager.get_user_by_email(email)
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409
    else:
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password)

        data_manager.create_user(new_user)

    print("✅ USER CREATED")
    return jsonify({"message": "user created successfully"}), 200


@app.route('/api/faq', methods=['POST'])
def generate_ai_response():
    data = request.get_json()
    user_prompt = data.get("user_prompt")
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": "Bitte antworte immer auf deutsch."},
            {"role": "user", "content": user_prompt}],
        max_output_tokens=50,
        temperature=0
    )
    return response.output_text


if __name__ == '__main__':
    # Create all tables when running app directly (for local development)
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5003, debug=False)
