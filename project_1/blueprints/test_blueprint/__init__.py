from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from project_1 import users, token_required

test_blueprint = Blueprint('test_blueprint', __name__)


@test_blueprint.route('/')
@token_required
def test_token(current_user):
    
    return users
    