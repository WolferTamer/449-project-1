# file dedicated to all routes involving user authorization and authentication
from flask import Blueprint, request, jsonify, session, current_app
from project_1 import locations, token_required, inventory
import re

# base blueprint for user. for our purposes it acts as an isolated app object that we can
# register to the main app. if you need to access the main app object, use current_app.
location = Blueprint('location', __name__)

def find_location(location_id, user):
    if user in locations:
        for place in locations[user]:
            if place["location_id"] == location_id:
                return place
    return None

# POST route for creating a new user. the body requires 'email', 'username', and 'password'
# 'password' requires at least 8 characters and a special character.
@location.route('/', methods=['GET'])
@token_required
def get_locations(current_user):
    if not current_user in locations:
        return jsonify({"error":"No Locations For This User"}), 404
    return jsonify(locations[current_user])

@location.route('/<int:location_id>', methods=['GET'])
@token_required
def get_location(current_user,location_id):
    if locations[current_user] != None:
        place = find_location(location_id, current_user)
        if place != None:
            return jsonify(place)
    return jsonify({"error":"Location Not Found"}), 404

@location.route('/', methods=['POST'])
@token_required
def create_location(current_user):
    required_fields = ['name', 'address', 'zip', 'state', 'capacity']
    if not request.json or not all(field in request.json for field in required_fields):
        return jsonify({'error': 'All fields are required: name, address, zip, state, and capacity'}), 400
    
    if not isinstance(request.json['name'], str):
        return jsonify({'error': 'name must be a string'}), 400
    if not isinstance(request.json['zip'], int) or request.json['zip'] > 99999 or request.json['zip'] < 0:
        return jsonify({'error': 'zip must be a positive 5 digit int'}), 400
    if not isinstance(request.json['capacity'], int):
        return jsonify({'error': 'capacity must be an int'}), 400
    if not isinstance(request.json['address'], str):
        return jsonify({'error': 'address must be a string'}), 400
    if not isinstance(request.json['state'], str) or len(request.json['state']) != 2:
        return jsonify({'error': 'state must be a string of 2 characters'}), 400
    
    loc_id = max((max((place['location_id'] for place in person), default=1) for person in locations.values()), default=1) + 1 if locations else 1
    new_location = {
        'location_id': loc_id,
        'name': request.json['name'],
        'zip': request.json['zip'],
        'capacity': request.json['capacity'],
        'address': request.json['address'],
        'state': request.json['state'],
    }
    locations[current_user].append(new_location)
    return jsonify(new_location), 201

@location.route('/<int:location_id>', methods=['PUT'])
@token_required
def update_location(current_user,location_id):
    place = find_location(location_id, current_user)
    if place is None:
        return jsonify({'error' : 'Place not found'}), 404
    
    if not request.json:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    if 'name' in request.json and not isinstance(request.json['name'], str):
        return jsonify({'error': 'name must be a str'}), 400
    if 'capacity' in request.json and not isinstance(request.json['capacity'], int):
        return jsonify({'ettor': 'quantity must be an int'}), 400
    if 'zip' in request.json and (not isinstance(request.json['zip'], int) and request.json['zip'] > 99999 or request.json['zip'] < 0):
        return jsonify({'error': 'price must be a float'}), 400
    if 'address' in request.json and not isinstance(request.json['address'], str):
        return jsonify({'error': 'description must be a string'})
    if 'state' in request.json and not isinstance(request.json['state'], str):
        return jsonify({'error': 'prescription_avail must be a bool'})
    
    place.update(request.json)
    return jsonify(place)

@location.route('/<int:location_id>', methods=['DELETE'])
@token_required
def delete_location(current_user,location_id):
    place = find_location(location_id, current_user)
    if place is None:
        return jsonify({'error': 'Location not found'}), 404
    inventory[current_user] = [x for x in inventory[current_user] if not x["location_id"] == location_id]
    locations[current_user].remove(place)
    return jsonify({'message': 'Location deletion successful'}), 200