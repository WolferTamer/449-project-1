# file used for defining all the enpoints/routes using blueprints
from project_1 import app
from project_1.blueprints.user import user
from project_1.blueprints.test_blueprint import test_blueprint

@app.route('/')
def index():
    return 'Hello 449!'

# register all blueprints to the app
# this may be changed later to automatically parse the files inside /blueprints
# so we don't have to manually add each one.
app.register_blueprint(user, url_prefix='/')
app.register_blueprint(test_blueprint,url_prefix='/test')