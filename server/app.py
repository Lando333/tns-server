#!/usr/bin/env python3

from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_session import Session
from config import ApplicationConfig
from models import db, User


# Instantiate app, set attributes
app = Flask(__name__)
app.config.from_object(ApplicationConfig)
app.json.compact = False



migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
server_session = Session(app)
db.init_app(app)

# Instantiate REST API, CORS
api = Api(app)
CORS(app)

@app.route('/')
def index():
    return 'Welcome to Tao Now Solutions!'



if __name__ == '__main__':
    app.run(port=5555, debug=True)
