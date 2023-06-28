#!/usr/bin/env python3

# Standard library imports
from random import randint, choice as rc
from random import sample

# Remote library imports
from faker import Faker
from datetime import datetime, timedelta, time

# Local imports
from app import app
from models import db, User, Address, Therapist, Service, Appointment,\
    therapist_services, user_appointment


if __name__ == '__main__':
    # fake = Faker()
    # now = datetime.now()

    with app.app_context():
        print("--Starting admin..--")

        # How to delete an object:
        therapist = Therapist.query.filter_by(therapist_id=5).first()
        if therapist:
            db.session.delete(therapist)
            db.session.commit()



        print("~Admin complete!~")
