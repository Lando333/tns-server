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

DURATIONS = [
    60,
    90
]

OFFERED_SERVICES = [
    'Swedish',
    'Deep Tissue',
    'Reflexology',
    'Acupuncture',
    'Acupressure'
]

if __name__ == '__main__':
    fake = Faker()
    now = datetime.now()

    with app.app_context():
        print("--Starting seed..--")

        Address.query.delete()
        User.query.delete()
        Therapist.query.delete()
        Service.query.delete()
        Appointment.query.delete()
        db.session.query(therapist_services).delete()
        db.session.query(user_appointment).delete()

        therapists = []
        for i in range(3):
            t = Therapist()
            therapists.append(t)

        addresses = []
        users = []
        for i in range(10):
            a = Address(
                address_line1 = fake.street_address(),
                city = fake.city(),
                state = fake.state(),
                zip_code = fake.postcode(),
                country = fake.current_country_code()
            )
            addresses.append(a)

            rand_therapist = rc(therapists)
            u = User(
                first_name = fake.first_name(),
                last_name = fake.last_name(),
                email = fake.email(),
                password = fake.word(),
                address = a,
                therapist = rand_therapist
            )
            users.append(u)

        services = []
        for t in OFFERED_SERVICES:
            s = Service(
                title = t,
                description = fake.paragraph(nb_sentences=1, variable_nb_sentences=False),
                price = randint(150, 275)
                )
            services.append(s)

        # Assign services to therapists
        for therapist in therapists:
            random_services = sample(services, k=3)
            therapist.services.extend(random_services)


        db.session.add_all(addresses)
        db.session.add_all(users)
        db.session.add_all(therapists)
        db.session.commit()


        appointments = []
        start_time = time(12, 0)
        end_time = time(20, 0) 
        working_hours_minutes = (end_time.hour - start_time.hour) * 60
        valid_minutes = [0, 30]
        for i in range(20):
            rand_user = rc(users)
            rand_t = rc(therapists)
            therapist_services = rand_t.services
            available_services = [service for service in therapist_services if service.title in OFFERED_SERVICES]
            random_service = rc(available_services)
            duration = rc(DURATIONS)

            # Generate a random date within the next 30 days
            appointment_date = now + timedelta(days=randint(1, 30))
            random_minutes = rc(valid_minutes)
            random_hour = randint(start_time.hour, end_time.hour)

            appointment_time = time(random_hour, random_minutes)
            appointment_datetime = datetime.combine(appointment_date, appointment_time)
            end_datetime = appointment_datetime + timedelta(minutes=duration)

            a = Appointment(
                therapist_id=rand_t.therapist_id,
                user_id=rand_user.user_id,
                service=random_service.title,
                duration=duration,
                appointment_time=appointment_time,
                appointment_date=appointment_datetime,
                end_datetime=end_datetime,
            )
            print("start "+str(a.appointment_date))
            print("time "+str(a.appointment_time))
            print("end "+str(a.end_datetime))
            print()
            appointments.append(a)
            a.users.append(rand_user)


        db.session.add_all(services)
        db.session.add_all(appointments)
        db.session.commit()



        #  ===== Checking therapists =====
        # for therapist in therapists:
        #     print(therapist.user.first_name)
        #     print(therapist.services)

        #  ===== Checking user appointments =====
        # for user in users:
        #     for appointment in user.user_appointments:
        #         print(appointment.appointment_date)
        #         if appointment.client:
        #             print('Client: ' + appointment.client.first_name)
        #         if appointment.therapist:
        #             print('Therapist: ' + appointment.therapist.user.first_name)
        #         if appointment.service:
        #             print('Service: ' + appointment.service)
        #         print()


        print("~Seeding complete!~")
