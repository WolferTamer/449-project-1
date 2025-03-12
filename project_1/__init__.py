from flask import Flask, jsonify, wrappers, request
from functools import wraps
app = Flask(__name__) 
__version__ = "0.0.1"
import jwt

import secrets
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)

users = {"coolguy":{'email':'coolguy@gmail.com','password':'coolp@ssword'}}

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
            print(data)
            if data['username'] in users:
                current_user = data['username']
            else:
                return jsonify({
                    'error' : 'Token is invalid'
                }), 401
        except:
            print("dead")
            return jsonify({
                'error' : 'Token is invalid'
            }), 401
        # returns the current logged in users context to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated

if __name__ == '__main__': 
    app.run()


import project_1.views