from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from project_1 import users

test_blueprint = Blueprint('test_blueprint', __name__)

@test_blueprint.route('/', defaults={'page': 'index'})
@test_blueprint.route('/<page>')
def show(page):
    return users
    