from flask import Flask 
app = Flask(__name__) 
__version__ = "0.0.1"

import secrets
app.secret_key = secrets.token_urlsafe(16)

users = {"coolguy":{'email':'coolguy@gmail.com','password':'coolp@ssword'}}

if __name__ == '__main__': 
    app.run()


import project_1.views