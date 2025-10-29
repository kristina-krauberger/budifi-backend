from flask import Flask, request, redirect
from data_manager import DataManager
from extentions import db
import requests
import os
from dotenv import load_dotenv

load_dotenv()


# 3 Tables = 3 models
# Routen anlegen user anlegen + postman testen

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/budifi.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Link the database and the app. This is the reason you need to import db from models

data_manager = DataManager(db) # Create an object of your DataManager class
