from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from data_manager import DataManager
from extentions import db
from flask_cors import CORS
import os


app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])
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

@app.route('/')
def hello_world():
  return jsonify({"message":"hello world"}), 200


@app.route('/api/courses')
def get_courses():
  courses = data_manager.list_courses()
  print(courses)
  #hier müssen alle Kursdaten rein und die komme aus Datamanager z.
  return jsonify(courses), 200



# @app.route('/api/user/<int:user_id>/dashboard', methods=['GET'])
# def show_user_dashboard(user_id):
#   """Shows dashboard including user progress."""
#   user_dashboard_data = data_manager.get_current_user_dashboard(user_id)
#   print(user_dashboard_data)
#   return jsonify(user_dashboard_data), 200
#
#
# @app.route('/api/course', methods=['GET'])
# def show_courses():
#   courses = data_manager.list_courses()
#   return jsonify(courses), 200
#

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



