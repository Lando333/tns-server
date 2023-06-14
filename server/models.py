from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime, Date, Time
from datetime import datetime

from app import db


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    address = db.relationship('Address', uselist=False, backref='user')
    appointments = db.relationship('Appointment', backref='user')


class Address(db.Model, SerializerMixin):
    __tablename__ = 'addresses'

    address_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    address_line1 = db.Column(db.String(50))
    address_line2 = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(5))
    country = db.Column(db.String(50))
    created_at = db.Column(DateTime, default=datetime.utcnow)


class Therapist(db.Model, SerializerMixin):
    __tablename__ = 'therapists'

    therapist_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    services_offered = db.relationship('Service', secondary='therapist_service_association')
    created_at = db.Column(DateTime, default=datetime.utcnow)


class Service(db.Model, SerializerMixin):
    __tablename__ = 'services'

    service_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    description = db.Column(db.String())
    price = db.Column(db.Integer)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    therapists = db.relationship('Therapist', secondary='therapist_service_association')


therapist_service_association = db.Table(
    'therapist_service_association',
    db.Column('therapist_id', db.Integer, db.ForeignKey('therapists.therapist_id')),
    db.Column('service_id', db.Integer, db.ForeignKey('services.service_id'))
)


class Appointment(db.Model, SerializerMixin):
    __tablename__ = 'appointments'

    appointment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    therapist_id = db.Column(db.Integer, db.ForeignKey('therapists.therapist_id'))
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'))
    appointment_date = db.Column(Date)
    appointment_time = db.Column(Time)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='appointments')
    therapist = db.relationship('Therapist', backref='appointments')
    service = db.relationship('Service', backref='appointments')
