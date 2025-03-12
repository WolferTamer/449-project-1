from project_1 import app
from project_1.blueprints.user import user

@app.route('/')
def index():
    return 'Hello 449!'

app.register_blueprint(user, url_prefix='/')