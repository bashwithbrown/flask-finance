import json

from flask import (Flask, render_template, url_for, redirect, Blueprint)
from flask_login import current_user, login_required

from core import config
from database import DatabaseManager
from functions import Logger

user = Blueprint('user', __name__, static_folder='../static/', template_folder='../templates/user')
logger = Logger(config)
database_manager = DatabaseManager(config.DATABASE)

@user.route('/', methods=['GET'])
def index():
    return redirect(url_for('user.profile'))

@user.route('/profile',  methods=['GET'])
def profile():
    return render_template('profile.html', user=current_user.__dict__, meta_data=json.loads(current_user.meta_data))