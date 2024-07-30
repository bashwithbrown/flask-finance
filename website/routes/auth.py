import json

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, logout_user, login_user

from core import config
from functions import generate_id
from database import DatabaseManager

auth = Blueprint('auth', __name__, static_folder='../static/', template_folder='../templates/auth')
database_manager = DatabaseManager(config.DATABASE)


@auth.route('/login', methods=['GET'])
def login():
    return render_template("login.html", site_key='')


@auth.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/reset-password', methods=['GET'])
@login_required
def reset_password():
    return render_template('reset-password.html', methods=['GET'])