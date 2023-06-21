#!/usr/bin/env python3

from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
from datetime import datetime
from models import db, User, Address, Therapist

# Instantiate app, set attributes
app = Flask(__name__)
app.config.from_object(ApplicationConfig)
app.json.compact = False

migrate = Migrate(app, db)
# Hashes password
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
db.init_app(app)

api = Api(app)


def get_user_id(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return user


@app.route('/')
def index():
    return 'Welcome to Tao Now Solutions!'

@app.route("/@me")
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    user = User.query.filter_by(user_id=user_id).first()
    return jsonify({
        "user_id": user.user_id,
        "email": user.email,
        "first_name":user.first_name.title()
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

    address_line1 = request.json["address_line1"]
    address_line2 = request.json["address_line2"]
    city = request.json["city"]
    state = request.json["state"]
    zip_code = request.json["zip_code"]
    country = request.json["country"]

    user_address = Address(
        user_id=new_user.user_id,

        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        zip_code=zip_code,
        country=country
    )
    db.session.add(user_address)
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
    user = get_user_id(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 202

@app.route("/create_therapist", methods=["POST"])
def create_therapist():
    email = request.json["email"]
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    new_therapist = Therapist(
        user_id=user.user_id
        )
    db.session.add(new_therapist)
    db.session.commit()
    return jsonify({"message": "Therapist created successfully"}), 201


if __name__ == '__main__':
    app.run(port=5555, debug=True)

