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
users = {"coolguy":{'email':'coolguy@gmail.com','password':'coolp@ssword'},
         "calebc":{'email':'calebc@gmail.com','password':'#password5'}}


locations = {"coolguy":[{"location_id":1,"name":"Cool Plaza Store","address":"5555 Cool Guy St",
                          "state":"CA", "zip":92222, "capacity":1000},
                        {"location_id":3,"name":"Overflow Location","address":"1234 Factory St",
                          "state":"CA", "zip":91234, "capacity":5000}],
            "calebc":[{"location_id":2,"name":"Caleb's Glasses Store","address":"987 Store Rd",
                          "state":"AZ", "zip":81356, "capacity":1500}]}


inventory = {
    "coolguy":[
        {"id": 1, "location_id": 1, "name": "Kevin", "quantity": 781, "price": 49.99, "description": "nice pair of glasses", 
            "prescription_avail": False, "tinted": False, "polarized": False, "width": 6.2, "anti_glare": False},
        {"id": 3, "location_id": 3, "name": "Bob", "quantity": 1225, "price": 34.99, "description": "Cheap glasses", 
            "prescription_avail": True, "tinted": False, "polarized": False, "width": 5.8, "anti_glare": True}
    ],
    "calebc":[ 
        {"id":2,"location_id":2,"name":"Custom Sunglasses","quantity":824,"price":64.99,"description":"cool custom sunglasses",
               "prescription_avail": False, "tinted": True, "polarized": True, "width":6.3, "anti-glare": False}
    ]
}

# Helper function to find glasses by ID
def find_glasses(glasses_id, user):
    if user in inventory:
        for glasses in inventory[user]:
            if glasses["id"] == glasses_id:
                return glasses
    return None

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

# Route to GET all glasses in inventory
@app.route('/inventory', methods=['GET'])
@token_required
def get_inventory(current_user):
    if current_user in inventory:
        return jsonify(inventory[current_user])
    else:
        return "No Inventory", 404

# Route to GET a specific pair of glasses in inventory
@app.route('/inventory/<int:glasses_id>', methods=['GET'])
@token_required
def get_glasses(current_user,glasses_id):
    glasses = find_glasses(glasses_id, current_user)
    if glasses is None:
        return jsonify({'error': 'Glasses not found'}), 404
    return jsonify(glasses)

@app.route('/inventory', methods=['POST'])
@token_required
def create_glasses(current_user):
    required_fields = ['location_id', 'name', 'quantity', 'price', 'description', 'prescription_avail', 'tinted', 'polarized', 'width', 'anti_glare']
    if not request.json or not all(field in request.json for field in required_fields):
        return jsonify({'error': 'All fields are required: location_id, name, quantity, price, description, prescription_avail, tinted, polarized, width, anti_glare'}), 400
    
    

    if not isinstance(request.json['location_id'], int):
        return jsonify({'error': 'location_id must be an int'}), 400
    potential_loc = None
    if current_user in locations:
        for location in locations[current_user]:
            if location["location_id"] == request.json['location_id']:
                potential_loc = location
    if potential_loc == None:
        return jsonify({'error': 'location_id must references a valid location'}), 400

    if not isinstance(request.json['name'], str):
        return jsonify({'error': 'name must be a string'}), 400
    if not isinstance(request.json['quantity'], int):
        return jsonify({'error': 'quantity must be an int'}), 400
    total = request.json['quantity']
    for g in inventory[current_user]:
        if g["location_id"] == request.json['location_id']:
            total+=g["quantity"]
    if total > potential_loc["capacity"]:
        return jsonify({'error': 'Exceeded location capacity'}), 400
    
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
    
    glasses_id = max((max((glass['id'] for glass in glasses),default=1) for glasses in inventory.values()),default=1) + 1 if inventory else 1
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
    inventory[current_user].append(glasses)
    return jsonify(glasses), 201

# Route to PUT an existing student
@app.route('/inventory/<int:glasses_id>', methods=['PUT'])
@token_required
def update_glasses(current_user,glasses_id):
    glasses = find_glasses(glasses_id, current_user)
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
    
    
    glasses_copy = glasses.copy()
    glasses_copy.update(request.json)
    potential_loc = None
    for location in locations[current_user]:
        if location["location_id"] == glasses_copy['location_id']:
            potential_loc = location
    
    total = glasses_copy['quantity']
    for g in inventory[current_user]:
        if g["location_id"] == glasses_copy['location_id']:
            total+=g["quantity"]
    if total > potential_loc["capacity"]:
        return jsonify({'error': 'Exceeded location capacity'}), 400


    glasses.update(request.json)
    return jsonify(glasses)

# Route to DELETE a student by ID
@app.route('/inventory/<int:glasses_id>', methods=['DELETE'])
@token_required
def delete_glasses(current_user,glasses_id):
    glasses = find_glasses(glasses_id, current_user)
    if glasses is None:
        return jsonify({'error': 'Glasses not found'}), 404
    inventory[current_user].remove(glasses)
    return jsonify({'message': 'Glasses deletion successful'}), 200
    

if __name__ == '__main__': 
    app.run()

# import at the end to prevent an import loop
import project_1.views