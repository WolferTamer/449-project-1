from flask import Flask 
app = Flask(__name__) 
__version__ = "0.0.1"
users = [{"id":1,"name":"Coolguy"}]

if __name__ == '__main__': 
    app.run()


import project_1.views