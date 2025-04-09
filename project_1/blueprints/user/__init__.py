# file dedicated to all routes involving user authorization and authentication
from flask import Blueprint, request, jsonify, session, current_app
from project_1 import users, token_required
import jwt
import datetime
from datetime import datetime, timedelta, timezone
import re

# base blueprint for user. for our purposes it acts as an isolated app object that we can
# register to the main app. if you need to access the main app object, use current_app.
user = Blueprint('users', __name__)

# Validate email format using a regular expression
def validate_email(email):  
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'  # Regex pattern for valid email
    return re.match(email_regex, email)  # Return a match object if the email matches the pattern, otherwise None

# POST route for creating a new user. the body requires 'email', 'username', and 'password'
# 'password' requires at least 8 characters and a special character.
@user.route('/register', methods=['POST'])
def register():
    # verify that all required parameters are included
    if not request.json or 'username' not in request.json or 'password' not in request.json or 'email' not in request.json:
        return jsonify({'error':'Username, password, and email are required to register a user.'}), 400
    
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']

    # check validity of all values
    # TODO: add check for email validity (xxx@yyy.zzz)
    if not validate_email(email):
        return jsonify({'error': 'Invalid email'})
    if not isinstance(username, str):
        return jsonify({'error':'Username must be a string'}), 400
    if not isinstance(password, str) or len(password) < 8 or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return jsonify({'error':'Password must be a string of at least 8 characters and contain at least one special character.'}), 400
    if username in users:
        return jsonify({'error':'Username is already in use.'}), 400
    
    # check that the email is not already in use
    email_values = []
    for key in users:
        email_values.append(users[key]["email"])
    if email in email_values:
        return jsonify({'error':'Email is already in use.'}), 400
    
    # add the new user to the object
    users[username] = {'email': email, 'password': password}
    return jsonify({'message':'User successfully created'}), 201

# login route. Only requires 'username' and 'password'. username may be switched out for email later on
# if login is successful, return a JWT for future authorization
@user.route('/login', methods=['POST'])
def login():
    # verify that all required parameters are included
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({'error':'Username and password are required to register a user.'}), 400
    username = request.json['username']
    password = request.json['password']

    # check validity of all values
    if not isinstance(username, str):
        return jsonify({'error':'Username must be a string'}), 400
    if not isinstance(password, str):
        return jsonify({'error':'Password must be a string'}), 400
    
    # if user does not exist or the password doesnt match, return 401
    if not users.get(username) or users.get(username).get('password') != password:
        return jsonify({'error': 'Invalid credentials'}), 401

    # if credentials correct, create a jwt that includes the username and a 30 minute expiry
    token = jwt.encode({
            'username': username,
            'exp' : datetime.now(timezone.utc) + timedelta(minutes=30)
        }, current_app.config['SECRET_KEY'])
    
    #start session
    session['user'] = username
    return jsonify({'message': 'Login successful', 'token':token}), 201

# No credentials required. Just pops the associated session.,
@user.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logout successful'}), 200

# refresh route is used to prevent token expiry. It returns a new jwt with the exp pushed back by another 30 minutes
@user.route('/refresh',methods=['GET'])
@token_required
def refresh(current_user):
    # setting this to true makes the session timeout reset without actually changing any values
    session.modified = True
    token = jwt.encode({
            'username': current_user,
            'exp' : datetime.now(timezone.utc) + timedelta(minutes=30)
        }, current_app.config['SECRET_KEY'])
    return jsonify({'message': 'Token Refreshed', 'token':token}), 201
    