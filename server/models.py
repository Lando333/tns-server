from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime, Date, Time
from datetime import datetime
from uuid import uuid4

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)

def get_uuid():
    return uuid4().hex


user_appointment = db.Table('user_appointment', 
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id')),
    db.Column('appointment_id', db.Integer, db.ForeignKey('appointments.appointment_id'))
)
therapist_services = db.Table(
    'therapist_services',
    db.Column('therapist_id', db.Integer, db.ForeignKey('therapists.therapist_id')),
    db.Column('service_id', db.Integer, db.ForeignKey('services.service_id'))
)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)

    address = db.relationship('Address', backref='user', uselist=False)
    therapist = db.relationship('Therapist', backref='user', uselist=False)
    appointments = db.relationship('Appointment', secondary=user_appointment, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return f'<User: {self.first_name} {self.last_name}'


class Address(db.Model, SerializerMixin):
    __tablename__ = 'addresses'

    address_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    address_line1 = db.Column(db.String(100), nullable=False)
    address_line2 = db.Column(db.String(50))
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)

class Therapist(db.Model, SerializerMixin):
    __tablename__ = 'therapists'

    therapist_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_at = db.Column(DateTime, default=datetime.utcnow)

    services = db.relationship('Service', secondary='therapist_services')


class Service(db.Model, SerializerMixin):
    __tablename__ = 'services'

    service_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), unique=True, nullable=False)
    description = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)


class Appointment(db.Model, SerializerMixin):
    __tablename__ = 'appointments'

    appointment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.user_id'))
    therapist_id = db.Column(db.Integer, db.ForeignKey('therapists.therapist_id'))
    service = db.Column(db.String, nullable=False)
    appointment_date = db.Column(Date, nullable=False)
    appointment_time = db.Column(Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    end_datetime = db.Column(Date, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)

    client = db.relationship('User', backref='user_appointments', foreign_keys=[user_id])
    therapist = db.relationship('Therapist', backref='therapist_appointments', foreign_keys=[therapist_id])

    def __init__(self, therapist_id, user_id, service, appointment_date, appointment_time, duration, end_datetime):
        self.therapist_id = therapist_id
        self.user_id = user_id
        self.service = service
        self.appointment_date = appointment_date
        self.appointment_time = appointment_time
        self.duration = duration
        self.end_datetime = end_datetime

