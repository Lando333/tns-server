#!/usr/bin/env python3

from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from flask_session import Session
from config import ApplicationConfig
from datetime import datetime
from models import db, User

# Instantiate app, set attributes
app = Flask(__name__)
app.config.from_object(ApplicationConfig)
app.json.compact = False

migrate = Migrate(app, db)
# Hashes password
bcrypt = Bcrypt(app)
server_session = Session(app)
CORS(app, supports_credentials=True)
db.init_app(app)

api = Api(app)


@app.route('/')
def index():
    return 'Welcome to Tao Now Solutions!'


@app.route("/@me")
def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        "id": user.id,
        "email": user.email
    }) 

@app.route("/register", methods=["POST"])
def register_user():
    email = request.json["email"]
    password = request.json["password"]
    first_name = request.json["first_name"]
    last_name = request.json["last_name"]

    user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({"error": "User already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password)
    new_user = User(
        email=email,
        password=hashed_password,
        first_name=first_name,
        last_name=last_name
        )
    db.session.add(new_user)
    db.session.commit()
    
    session["user_id"] = new_user.user_id

    return jsonify({
        "id": new_user.user_id,
        "email": new_user.email
    }), 201

@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401
    
    session["user_id"] = user.user_id

    return jsonify({
        "user_id": user.user_id,
        "email": user.email
    })

@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id")
    return "200"


@app.route("/delete/<string:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.filter_by(user_id=user_id).first()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 202




if __name__ == '__main__':
    app.run(port=5555, debug=True)

