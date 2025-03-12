from project_1 import app
from project_1.blueprints.user import user
from project_1.blueprints.test_blueprint import test_blueprint

@app.route('/')
def index():
    return 'Hello 449!'

app.register_blueprint(user, url_prefix='/')
app.register_blueprint(test_blueprint,url_prefix='/test')