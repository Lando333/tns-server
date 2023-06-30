#!/usr/bin/env python3

import json
from flask import Flask, request, jsonify, session, url_for, redirect
from flask_login import current_user
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from flask_restful import Api, Resource, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
from datetime import datetime, timedelta
from models import db, User, Address, Therapist, Appointment, Service, Schedule
import re
import stripe

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
stripe.api_key = app.config['STRIPE_SECRET_KEY']


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
    address_line1 = request.json["address_line1"]
    address_line2 = request.json["address_line2"]
    city = request.json["city"]
    state = request.json["state"]
    zip_code = request.json["zip_code"]

    if not (isinstance(first_name, str) and len(first_name) >= 1):
        return jsonify({"error": "First name must be a string with at least 1 character"}), 400
    if not (isinstance(last_name, str) and len(last_name) >= 1):
        return jsonify({"error": "Last name must be a string with at least 1 character"}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email"}), 400
    if len(password) < 5:
        return jsonify({"error": "Password must have at least 5 characters"}), 400
    if len(zip_code) != 5:
        return jsonify({"error": "Invalid zip code"}), 400
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

    user_address = Address(
        user_id=new_user.user_id,

        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        zip_code=zip_code,
        country='US'
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
        "therapist_id": therapist.therapist_id,
        "user_id":therapist.user_id
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

@app.route("/get_therapist_schedule/<int:therapist_id>")
def get_therapist_schedule(therapist_id):
    # therapist_id = request.json["selectedTherapistId"]
    print(therapist_id)

    therapist = Therapist.query.filter_by(therapist_id=therapist_id).first()
    if not therapist:
        return jsonify({"error": "Therapist unavailable."}), 400
    schedule = Schedule.query.filter_by(therapist_id=therapist_id).all()
    schedule_data = []
    for entry in schedule:
        schedule_data.append({
            "schedule_id": entry.schedule_id,
            "day_of_week": entry.day_of_week,
            "start_time": entry.start_time,
            "end_time": entry.end_time
        })
    return jsonify({"schedule": schedule_data}), 200


@app.route("/check_schedule", methods=["POST"])
def check_schedule():
    user_id = request.json["user_id"]
    therapist_id = request.json["therapist_id"]
    service = request.json["service"]
    duration = request.json["duration"]
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
    if isinstance(duration, str):
        return jsonify({"error": "How long would you like your service to last?"}), 400

    existing_appointments = Appointment.query.filter_by(therapist_id=therapist_id).all()
    for appointment in existing_appointments:
        if appointment.appointment_date == start:
            appointment_time = appointment.appointment_time.split(":")
            appointment_hour = int(appointment_time[0])
            time_hour = int(time.split(":")[0])
            if appointment_hour == time_hour or appointment_hour +1 == time_hour or appointment_hour -1 == time_hour:
                return jsonify({"error": "That time is unavailable. Please try a different time or therapist."}), 400
    return jsonify({"message": "Schedule is available"}), 200

@app.route("/create_appointment", methods=["POST"])
def create_appointment():
    user_id = request.json["user_id"]
    therapist_id = request.json["therapist_id"]
    service = request.json["service"]
    duration = int(request.json["duration"])
    time = request.json["time"]
    start = request.json["start"]

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

    # Check if all start and end times are empty
    if all(not day_data['startTime'] and not day_data['endTime'] for day_data in updated_schedule.values()):
        return jsonify({"error": "Please fill in your schedule!"}), 400

    valid_therapist = Therapist.query.filter_by(user_id=user_id).first()
    if valid_therapist:
        schedules = []
        for day, data in updated_schedule.items():
            start_time = data['startTime']
            end_time = data['endTime']
            # Check if both start and end times are empty
            if not start_time and not end_time:
                continue 
            # Check if either start or end time is missing
            if not start_time or not end_time:
                return jsonify({"error": "Invalid schedule update"}), 400
            schedule = Schedule(
                therapist_id=valid_therapist.therapist_id,
                day_of_week=day.title(),
                start_time=start_time,
                end_time=end_time
            )
            schedules.append(schedule)

        # Delete existing schedules for the therapist
        Schedule.query.filter_by(therapist_id=valid_therapist.therapist_id).delete()

        db.session.add_all(schedules)
        db.session.commit()
        return jsonify({"message": "Schedule updated successfully"}), 200
    else:
        return jsonify({"error": "Invalid user"}), 400

@app.route("/tx60")
def treatment_sixty():
    stripe_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1NNeRBIsiLf1acuK3Pb3UYXb',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return jsonify({
        "message": "Treatment booked successfully",
        "session_id": stripe_session.id
    }), 200

@app.route("/tx90")
def treatment_ninety():
    stripe_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1NNeS6IsiLf1acuKVvIQ1Rwt',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('/@me', _external=True),
    )
    return jsonify({
        "message": "Treatment booked successfully",
        "session_id": stripe_session.id
    }), 200

@app.route("/thanks", methods=['GET'])
def thanks():
    session_id = request.args.get('session_id')
    if session_id:
        return redirect("http://localhost:3000/thanks")
    return jsonify({"message": "Event received"}), 200


@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)

    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'whsec_e623208b34cb811c9ab8ddc606d34c017a21da9a0730c2d9c8d45cde8d27bff5'
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        print('INVALID SIGNATURE')
        return {}, 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items['data'][0]['description'])

    return {}




if __name__ == '__main__':
    app.run(port=5555, debug=True)

