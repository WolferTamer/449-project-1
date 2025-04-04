from flask import Flask, jsonify, wrappers, request, session
from functools import wraps
from datetime import datetime, timezone, timedelta

app = Flask(__name__) 
__version__ = "0.0.1"
import re
import jwt

import secrets
# makes it so that every session automatically expires after 30 minutes
app.permanent_session_lifetime = timedelta(minutes=30)
# generates a random 256 bit token to use a secret key
# this makes it so that the key changes every time the server is run
# to make it more convenient, we may switch this to use a config.py file with a premade token
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)


# user object used to store data. Can be imported into other files. 
# FORMAT:
# username: {'email':'email_value', 'password':'password_value'}
users = {"coolguy":{'email':'coolguy@gmail.com','password':'coolp@ssword'}}

# TODO:
# Create an inventory object for storing inventory information.
# Each inventory object must be associated with a username
# Other values TBD
inventory = [
    {"id": 1, "location_id": 714, "name": "Kevin", "quantity": 781, "price": 49.99, "description": "nice pair of glasses", 
     "prescription_avail": False, "tinted": False, "polarized": False, "width": 6.2, "anti_glare": False}
]

# Helper function to find glasses by ID
def find_glasses(glasses_id):
    for glasses in inventory:
        if glasses["id"] == glasses_id:
            return glasses
    return None

# Route to GET all glasses in inventory
@app.route('/inventory', methods=['GET'])
def get_inventory():
    return jsonify(inventory)

# Route to GET a specific pair of glasses in inventory
@app.route('/inventory/<int:glasses_id>', methods=['GET'])
def get_glasses(glasses_id):
    glasses = find_glasses(glasses_id)
    if glasses is None:
        return jsonify({'error': 'Glasses not found'}), 404
    return jsonify(glasses)

@app.route('/inventory', methods=['POST'])
def create_glasses():
    required_fields = ['location_id', 'name', 'quantity', 'price', 'description', 'prescription_avail', 'tinted', 'polarized', 'width', 'anti_glare']
    if not request.json or not all(field in request.json for field in required_fields):
        return jsonify({'error': 'All fields are required: location_id, name, quantity, price, description, prescription_avail, tinted, polarized, width, anti_glare'}), 400
    
    if not isinstance(request.json['location_id'], int):
        return jsonify({'error': 'location_id must be an int'}), 400
    if not isinstance(request.json['name'], str):
        return jsonify({'error': 'name must be a string'}), 400
    if not isinstance(request.json['quantity'], int):
        return jsonify({'error': 'quantity must be an int'}), 400
    if not isinstance(request.json['price'], float):
        return jsonify({'error': 'price must be a float'}), 400
    if not isinstance(request.json['description'], str):
        return jsonify({'error': 'description must be a string'}), 400
    if not isinstance(request.json['prescription_avail'], bool):
        return jsonify({'error': 'prescription_avail must be a bool'}), 400
    if not isinstance(request.json['tinted'], bool):
        return jsonify({'error': 'tinted must be an bool'}), 400
    if not isinstance(request.json['polarized'], bool):
        return jsonify({'error': 'polarized must be a bool'}), 400
    if not isinstance(request.json['width'], float):
        return jsonify({'error': 'width must be a float'}), 400
    if not isinstance(request.json['anti_glare'], bool):
        return jsonify({'error': 'anti_glare must be a bool'}), 400
    
    glasses_id = max(glasses['id'] for glasses in inventory) + 1 if inventory else 1
    glasses = {
        'id': glasses_id,
        'location_id': request.json['location_id'],
        'name': request.json['name'],
        'quantity': request.json['quantity'],
        'price': request.json['price'],
        'description': request.json['description'],
        'prescription_avail': request.json['prescription_avail'],
        'tinted': request.json['tinted'],
        'polarized': request.json['polarized'],
        'width': request.json['width'],
        'anti_glare': request.json['anti_glare'],
    }
    inventory.append(glasses)
    return jsonify(glasses), 201

# Route to PUT an existing student
@app.route('/inventory/<int:glasses_id>', methods=['PUT'])
def update_glasses(glasses_id):
    glasses = find_glasses(glasses_id)
    if glasses is None:
        return jsonify({'error' : 'Glasses not found'}), 404
    
    if not request.json:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    if 'location_id' in request.json and not isinstance(request.json['location_id'], int):
        return jsonify({'error': 'location_id must be an int'}), 400
    if 'name' in request.json and not isinstance(request.json['name'], str):
        return jsonify({'error': 'name must be a str'}), 400
    if 'quantity' in request.json and not isinstance(request.json['quantity'], int):
        return jsonify({'ettor': 'quantity must be an int'}), 400
    if 'price' in request.json and not isinstance(request.json['price'], float):
        return jsonify({'error': 'price must be a float'}), 400
    if 'description' in request.json and not isinstance(request.json['description'], str):
        return jsonify({'error': 'description must be a string'})
    if 'prescription_avail' in request.json and not isinstance(request.json['prescription_avail'], bool):
        return jsonify({'error': 'prescription_avail must be a bool'})
    if 'tinted' in request.json and not isinstance(request.json['tinted'], bool):
        return jsonify({'error': 'tinted must be a bool'})
    if 'polarized' in request.json and not isinstance(request.json['polarized'], bool):
        return jsonify({'error': 'polarized must be a bool'})
    if 'width' in request.json and not isinstance(request.json['width'], float):
        return jsonify({'error': 'width must be a floant'})
    if 'anti_glare' in request.json and not isinstance(request.json['anti_glare'], bool):
        return jsonify({'error': 'anti_glare must be a bool'})
    
    glasses.update(request.json)
    return jsonify(glasses)

# Route to DELETE a student by ID
@app.route('/inventory/<int:glasses_id>', methods=['DELETE'])
def delete_glasses(glasses_id):
    glasses = find_glasses(glasses_id)
    if glasses is None:
        return jsonify({'error': 'Glasses not found'}), 404
    inventory.remove(glasses)
    return jsonify({'message': 'Glasses deletion successful'}), 200
    

# token_required decorator that checks for a JWT in the headers
# Uses the format of Authorization: Bearer xxx.yyy.zzz
# Token expiry is 30 minutes and is handled automatically by jwt.decode()
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'Authorization' in request.headers:
            temp_token = request.headers['Authorization']
            prefix = 'Bearer '
            if not temp_token.startswith(prefix):
                return jsonify({'error':'Token is Invalid'})
            token = temp_token[len(prefix):]
        # return 401 if token is not passed
        if not token:
            return jsonify({'error' : 'Token is missing'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # check that the user exists and is associated with the current session
            if data['username'] in users and session['user'] == data['username']:
                current_user = data['username']
            # return 401 if not pased
            else:
                return jsonify({
                    'error' : 'Token is invalid'
                }), 401
        # end the session if the token has expired, return 401
        except jwt.ExpiredSignatureError:
            session.pop('user', None)
            return jsonify({
                'error':'Token is expired'
            }), 401
        except:
            return jsonify({
                'error' : 'Token is invalid'
            }), 401
        # returns the current logged in users context to the routes
        return  f(current_user, *args, **kwargs)

    return decorated

if __name__ == '__main__': 
    app.run()

# import at the end to prevent an import loop
import project_1.views