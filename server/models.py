from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime, Date, Time
from datetime import datetime

from config import db

# Models go here!
class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String)
    created_at = db.Column(DateTime, default=datetime.utcnow)


class Therapist(db.Model, SerializerMixin):
    __tablename__ = 'therapists'

    therapist_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    services_offered = db.Column(db.String, db.ForeignKey('services.title'))
    created_at = db.Column(DateTime, default=datetime.utcnow)


class Address(db.Model, SerializerMixin):
    __tablename__ = 'addresses'

    address_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    address_line1 = db.Column(db.String(50))
    address_line2 = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip_code  = db.Column(db.String(5))
    country  = db.Column(db.String(50))
    created_at = db.Column(DateTime, default=datetime.utcnow)


class Service(db.Model, SerializerMixin):
    __tablename__ = 'services'

    service_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    description = db.Column(db.String())
    price = db.Column(db.Integer)
    created_at = db.Column(DateTime, default=datetime.utcnow)


class Appointment(db.Model, SerializerMixin):
    __tablename__ = 'appointments'

    appointment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    therapist_id = db.Column(db.Integer, db.ForeignKey('therapists.therapist_id'))
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'))
    appointment_date = db.Column(db.Date)
    appointment_time = db.Column(db.Time)
    created_at = db.Column(DateTime, default=datetime.utcnow)

