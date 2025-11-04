from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from data_manager import DataManager
from datetime import datetime
from extentions import db
import os


app = Flask(__name__)
bcrypt = Bcrypt(app)  # initiates bcrypt für hashing password

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/budifi.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Links the database and the App

data_manager = DataManager(db) # Creates an object of your DataManager Class


@app.route('/api/signup', methods=['POST'])
def add_user():
  """Adds a new user to the database from form input."""
  data = request.get_json()
  first_name = data.get('first_name')
  last_name = data.get('last_name')
  email = data.get('email')
  password = data.get('password')
  hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
  new_user = User(
    first_name=first_name,
    last_name=last_name,
    email=email,
    password=hashed_password)

  data_manager.create_user(new_user)

  return jsonify({"message":"user created successfully"}), 200


@app.route('/api/user/<int:user_id>/dashboard', methods=['GET'])
def show_user_dashboard(user_id):
  """Shows dashboard including user progress."""

  # ÜBERSETZT: Hol mir mit .get() aus der "User" Tabelle die Instanz mit PRIMÄRSCHLÜSSEL "user_id" = 1 und pack in Variable "user"
  user = User.query.get(user_id)
  first_name = user.first_name
  print(f"User: {user}, {type(user)}")
  print(f"First: {first_name}, {type(first_name)}, {len(first_name)}")

  # ÜBERSETZT: Hol mir aus der "Enrollment" JOINT-Tabelle durch FILTERUNG der "user_id" = user_id und pack Instanz in Variable "enrollment"
  # ÜBERSETZT: .all() gib mir alle Spalten zu User 3 (Lina hat 3 Kurse belegt)
  enrollment = Enrollment.query.filter_by(user_id=user_id).all()
  progress_per_course = [progress.progress for progress in enrollment]
  print(f"Enrollment: {enrollment}, {type(enrollment)}")
  print(f"Progress: {progress_per_course}, {type(progress_per_course)}")

  # Shows days of enrolment for each user since signup.
  enrolled_at = enrollment[0].enrolled_at
  days_since_enrolled = (datetime.utcnow() - enrolled_at).days
  print(f"Enrolled at: {enrolled_at}, {type(enrolled_at)}")
  print(f"Enrolled since '{days_since_enrolled}' days! {type(days_since_enrolled)}")

  user_dashboard_data = {
    "user_id": user.id,
    "first_name": first_name,
    "days_since_enrolled": days_since_enrolled,
    "courses": []
  }

  return jsonify(user_dashboard_data), 200



if __name__ == '__main__':
  with app.app_context():
    from models.user import User
    from models.course import Course
    from models.enrollment import Enrollment
    db.create_all()

  app.run(host="0.0.0.0", port=5002, debug=True)



