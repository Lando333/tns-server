#!/usr/bin/env python3

# Remote library imports
from faker import Faker

# Local imports
from app import app
from models import db, User, Address, Therapist, Service, Appointment,\
    therapist_services, user_appointment


if __name__ == '__main__':
    fake = Faker()

    with app.app_context():
        print("--Starting admin..--")

        # How to delete an object:
        therapist = Therapist.query.filter_by(therapist_id=4).first()
        if therapist:
            db.session.delete(therapist)
            db.session.commit()

        # Adding services to therapist:
        services = Service.query.all()
        therapist = Therapist.query.filter_by(therapist_id=4).first()
        if therapist:
            for service in services:
                therapist.services.append(service)
            db.session.add(therapist)
            db.session.commit()

        # Editing object values
        ryan = User.query.filter_by(user_id="b0f0e3f1d0a3413eacfcc21b7a9dd05d").first()
        ryan.first_name = 'Ryan'
        ryan.last_name = 'Rojas'
        ryan.email = 'ryan@gmail.com'
        db.session.add(ryan)
        db.session.commit()


        print("~Admin complete!~")
