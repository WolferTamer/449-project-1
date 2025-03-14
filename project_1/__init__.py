from flask import Flask, jsonify, wrappers, request, session
from functools import wraps
from datetime import datetime, timezone, timedelta
app = Flask(__name__) 
__version__ = "0.0.1"
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