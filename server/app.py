#!/usr/bin/env python3

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import MetaData
from datetime import datetime

# Instantiate app, set attributes
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Import models


# Define metadata, instantiate db
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)
migrate = Migrate(app, db)
db.init_app(app)

# Instantiate REST API, CORS
api = Api(app)
CORS(app)

@app.route('/')
def index():
    return 'Welcome to Tao Now Solutions!'

# Create the User resource
class UserResource(Resource):
    def post(self):
        from models import User
        # Parse and validate the request data
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str, required=True, help='First name is required')
        parser.add_argument('last_name', type=str, required=True, help='Last name is required')
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        args = parser.parse_args()

        # Create a new User instance
        user = User(first_name=args['first_name'], last_name=args['last_name'], email=args['email'], password=args['password'], created_at=datetime.utcnow())

        try:
            # Save the user to the database
            db.session.add(user)
            db.session.commit()
            
            # Return the serialized user data
            user_data = user.to_dict()
            return {'message': 'User registered successfully', 'user': user_data}, 201
        except IntegrityError:
            # Handle integrity constraint violation (e.g., duplicate email)
            db.session.rollback()
            return {'error': 'Email already exists'}, 409
        except Exception as e:
            # Handle other exceptions
            db.session.rollback()
            return {'error': str(e)}, 500


# Create the Address resource
class AddressResource(Resource):
    def post(self):
        from models import User, Address
        # Parse and validate the request data
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True, help='User ID is required')
        parser.add_argument('address_line1', type=str, required=True, help='Address line 1 is required')
        parser.add_argument('address_line2', type=str)
        parser.add_argument('city', type=str, required=True, help='City is required')
        parser.add_argument('state', type=str, required=True, help='State is required')
        parser.add_argument('zip_code', type=str, required=True, help='ZIP code is required')
        parser.add_argument('country', type=str, required=True, help='Country is required')
        args = parser.parse_args()

        # Check if the user exists
        user = User.query.get(args['user_id'])
        if not user:
            return {'error': 'User not found'}, 404

        # Create a new Address instance
        address = Address(user_id=args['user_id'],
            address_line1=args['address_line1'],
            address_line2=args['address_line2'],
            city=args['city'],
            state=args['state'],
            zip_code=args['zip_code'],
            country=args['country'],
            created_at=datetime.utcnow()
        )

        try:
            # Save the address to the database
            db.session.add(address)
            db.session.commit()
            # Return the serialized address data
            address_data = address.to_dict()
            return {'message': 'Address added successfully', 'address': address_data}, 201
        except Exception as e:
            # Handle exceptions
            db.session.rollback()
            return {'error': str(e)}, 500


# Add the User and Address resources to the API
api.add_resource(UserResource, '/users')
api.add_resource(AddressResource, '/addresses')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
