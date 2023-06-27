#!/usr/bin/env python3
import pytz
from flask import Flask, request, jsonify, session
from flask_login import current_user
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
from datetime import datetime, timedelta
from models import db, User, Address, Therapist, Appointment, Service, Schedule

# Instantiate app, set attributes
app = Flask(__name__)
app.config.from_object(ApplicationConfig)
app.json.compact = False

migrate = Migrate(app, db)
# Hashes password
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])
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

@app.route("/all_therapists")
def get_therapists():
    therapists = Therapist.query.all()
    therapist_data = [{
        "name": therapist.user.first_name + " " + therapist.user.last_name[:1] + ".",
        "services": [service.title for service in therapist.services],
        "therapist_id": therapist.therapist_id
    } for therapist in therapists]
    return jsonify(therapist_data), 200

@app.route("/all_appointments")
def get_all_appointments():
    appointments = Appointment.query.all()
    appointment_data = []
    
    for appointment in appointments:
        therapist = Therapist.query.get(appointment.therapist_id)
        user = User.query.get(appointment.user_id)

        appointment_dict = {
            'title': f'{therapist.user.first_name} - {appointment.service} - {appointment.duration}',
            'appointment_id': appointment.appointment_id,
            'client': f'{user.first_name} {user.last_name}',
            'therapist_id': appointment.therapist_id,
            'therapist_name': f'{therapist.user.first_name} {therapist.user.last_name}',
            'service': appointment.service,
            'duration': appointment.duration,
            'start': f'{appointment.appointment_date} {appointment.appointment_time}',
            'time': appointment.appointment_time,
            'created_at': appointment.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
        }
        appointment_data.append(appointment_dict)
    
    return jsonify(appointment_data), 200


@app.route("/therapist_services/<therapist_name>")
def get_therapist_services(therapist_name):
    therapist_name = therapist_name.split()[0]  # Extract only the first name
    therapist = Therapist.query.join(User).filter(User.first_name == therapist_name).first()
    if therapist:
        services = [service.title for service in therapist.services]
        return jsonify(services)
    return jsonify({"error":"No services found."}), 404


@app.route("/create_appointment", methods=["POST"])
def create_appointment():
    user_id = request.json["user_id"]
    therapist_id = request.json["therapist_id"]
    service = request.json["service"]
    duration = int(request.json["duration"])
    time = request.json["time"]
    start = request.json["start"]

    # Validate the event data
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"error": "Invalid user ID"}), 400

    therapist = Therapist.query.filter_by(therapist_id=therapist_id).first()
    if not therapist:
        return jsonify({"error": "Don't forget your therapist!"}), 400
    
    serv = Service.query.filter_by(title=service).first()
    if not serv:
        return jsonify({"error": "Please choose a service!"}), 400

    existing_appointments = Appointment.query.filter_by(therapist_id=therapist_id).all()
    for appointment in existing_appointments:
        if appointment.appointment_date == start:
            appointment_time = appointment.appointment_time.split(":")
            appointment_hour = int(appointment_time[0])
            time_hour = int(time.split(":")[0])
            if appointment_hour == time_hour or appointment_hour +1 == time_hour or appointment_hour -1 == time_hour:
                return jsonify({"error": "That time is unavailable. Please try a different time or therapist."}), 400

    # Create the appointment
    appointment = Appointment(
        user_id=user_id,
        therapist_id=therapist_id,
        service=service,
        duration=duration,
        appointment_date=start,
        appointment_time=time,
    )
    print(appointment)
    db.session.add(appointment)
    db.session.commit()

    return jsonify({"message": "Appointment created successfully"}), 201


@app.route('/update_schedule', methods=['POST'])
def update_schedule():
    user_id = request.json.get('userId')
    updated_schedule = request.json.get('updatedSchedule')
    valid_user = User.query.filter_by(user_id=user_id).first()
    valid_therapist = Therapist.query.filter_by(user_id=valid_user.user_id).first()
    if valid_therapist and updated_schedule:
        Schedule.query.filter_by(therapist_id=valid_therapist.therapist_id).delete()
        schedules = []
        for day, data in updated_schedule.items():
            schedule = Schedule(
                therapist_id=valid_therapist.therapist_id,
                day_of_week=day.title(),
                start_time=data['startTime'],
                end_time=data['endTime']
            )
            schedules.append(schedule)

        # Add the new schedules to the database
        db.session.add_all(schedules)
        db.session.commit()

        return jsonify({"message": "Schedule updated successfully"}), 200
    else:
        return jsonify({"error": "Invalid request"}), 400



if __name__ == '__main__':
    app.run(port=5555, debug=True)

