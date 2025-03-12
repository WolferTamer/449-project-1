from flask import Blueprint, request, jsonify, session, current_app
from project_1 import users
import jwt
import datetime
from datetime import datetime, timedelta, timezone
import re

user = Blueprint('users', __name__)

@user.route('/register', methods=['POST'])
def register():
    if not request.json or 'username' not in request.json or 'password' not in request.json or 'email' not in request.json:
        return jsonify({'error':'Username, password, and email are required to register a user.'}), 400
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']

    if not isinstance(username, str):
        return jsonify({'error':'Username must be a string'})
    if not isinstance(password, str) or len(password) < 8 or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return jsonify({'error':'Password must be a string of at least 8 characters and contain at least one special character.'})
    if username in users:
        return jsonify({'error':'Username is already in use.'})
    email_values = []
    for key in users:
        email_values.append(users[key]["email"])
    if email in email_values:
        return jsonify({'error':'Email is already in use.'})
    
    users[username] = {'email': email, 'password': password}
    return jsonify({'message':'User successfully created'}), 201

@user.route('/login', methods=['POST'])
def login():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'error':'Username and password are required to register a user.'}), 400
    username = request.json['username']
    password = request.json['password']

    if not isinstance(username, str):
        return jsonify({'error':'Username must be a string'})
    if not isinstance(password, str) or len(password) < 8 or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return jsonify({'error':'Password must be a string of at least 8 characters and contain at least one special character.'})
    
    if not users.get(username) or users.get(username).get('password') != password:
        return jsonify({'error': 'Invalid credentials'}), 401

    token = jwt.encode({
            'username': username,
            'exp' : datetime.now(timezone.utc) + timedelta(minutes = 30)
        }, current_app.config['SECRET_KEY'])
    session['user'] = username
    return jsonify({'message': 'Login successful', 'token':token}), 201

@user.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logout successful'}), 200