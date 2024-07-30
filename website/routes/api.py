import os
import json
import requests
import datetime as dt
from collections import defaultdict

from flask import (Flask, render_template, request, url_for, redirect, jsonify, flash, Blueprint)
from flask_login import login_required, current_user, login_user

from core import config
from database import DatabaseManager
from functions import Logger, generate_id, allowed_file, log_api_error, calculate_returns, retreive_transactions_from_db, get_eth_to_usd_rate

from werkzeug.utils import secure_filename


api = Blueprint('api', __name__)
logger = Logger(config)
database_manager = DatabaseManager(config.DATABASE)

    
# start: TRANSACTION
@api.route('/submit-transaction-information', methods=['POST'])
@login_required
def submit_transaction_information():
    try:
        with database_manager as session:
            transaction = database_manager.Transaction(
                id=generate_id('string'),
                date=dt.datetime.now(),
                amount=request.form['amount'],
                category=request.form['category'],
                notes=request.form['description'],
            )

            session.add(transaction)
            session.commit()

            return redirect(url_for('finance.transactions'), code=302)

    except Exception as exc:
        log_api_error(logger, exc, request)
        return redirect(url_for('finance.transactions'), code=302)

@api.route('alter-transaction-information/<string:transaction_id>', methods=['POST'])
@login_required
def alter_transaction_information(transaction_id):
    try:
        with database_manager as session:
            transaction = session.query(database_manager.Transaction).filter_by(id=transaction_id).first()
            transaction.name = request.form['amount']
            transaction.category = request.form['category']
            transaction.notes = request.form['description']
            session.commit()

        return redirect(url_for('finance.transactions'), code=302)


    except Exception as exc:
        log_api_error(logger, exc, request)
        return redirect(url_for('finance.transactions'), code=302)


@api.route('delete-transaction-information/<string:transaction_id>', methods=['POST'])
@login_required
def delete_transaction_information(transaction_id):
    try:

        with database_manager as session:
            session.delete(session.query(database_manager.Transaction).filter_by(id=transaction_id).first())
            session.commit()

        return redirect(url_for('finance.transactions'), code=302)


    except Exception as exc:
        log_api_error(logger, exc, request)
        return redirect(url_for('finance.transactions'), code=302)

# end: TRANSACTION


# start: CHART
@api.route('/get-line-chart-data', methods=['GET'])
@login_required
def get_chart_data():
    sorted_transactions = sorted(retreive_transactions_from_db(database_manager)[0], key=lambda transaction: transaction.date)

    if config.INSTANCE_META_DATA.get('timeline', '') == 'ytd':
        sorted_transactions = [tx for tx in sorted_transactions if tx.date > dt.datetime(dt.datetime.now().year, 1, 1)]

    values = [float(transaction.amount) if transaction.category_type == "INCOME" else -float(transaction.amount) for transaction in sorted_transactions]
    dates = [str(transaction.date) for transaction in sorted_transactions]
    data = {
        'labels': dates,
        'values': calculate_returns(values)
    }

    return jsonify(data)

@api.route('/get-doughnut-chart-data', methods=['GET'])
@login_required
def get_doughnut_chart_data():
    sorted_transactions = sorted(retreive_transactions_from_db(database_manager)[0], key=lambda transaction: transaction.date)
    if config.INSTANCE_META_DATA.get('timeline', '') == 'ytd':
        sorted_transactions = [tx for tx in sorted_transactions if tx.date > dt.datetime(dt.datetime.now().year, 1, 1)]


    chart_data = defaultdict(float)

    for tx in sorted_transactions:
        chart_data[tx.category] += tx.amount

    data = {
        'labels': list(chart_data.keys()),
        'values': list(chart_data.values())
    }

    return jsonify(data)
# end: CHART



# start: USER
@api.route('alter-user-information/<string:user_id>', methods=['POST'])
@login_required
def alter_user_information(user_id):
    try:
        with database_manager as session:
            user = session.query(database_manager.User).filter_by(id=user_id).first()
            
            user.username = request.form.get('username', '')
            user.meta_data = json.loads(user.meta_data)
            user.meta_data['email'] = request.form.get('email', '')
            user.meta_data['is_admin'] = 'True' if request.form.get('is_admin', '') else "False"
            user.meta_data['is_employee'] = 'True' if request.form.get('is_employee', '') else "False"
            user.meta_data['kraken_api_key'] = request.form.get('kraken_api_key', '')
            user.meta_data['kraken_api_secret'] = request.form.get('kraken_api_secret', '')
            user.meta_data['etherscan_api_key'] = request.form.get('etherscan_api_key', '')
            user.meta_data['ethereum_wallet_address'] = request.form.get('ethereum_wallet_address', '')
            user.meta_data = json.dumps(user.meta_data)
            session.commit()

        return redirect(url_for('user.profile'), code=302)

    except Exception as exc:
        log_api_error(logger, exc, request)
        return redirect(url_for('user.profile'), code=302)




@api.route('/alter-user-profile-picture/<string:user_id>', methods=['POST'])
@login_required
def alter_user_profile_picture(user_id):
    try:

        file = request.files['file']
        if not allowed_file(file.filename, config.ALLOWED_EXTENSIONS):
            flash('File type not allowed.', 'error')
            return redirect(url_for('user.profile'), code=302)
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(config.FILE_UPLOAD_DIR, filename))

            with database_manager as session:
                user = session.query(database_manager.User).filter_by(id=user_id).first()

                user.meta_data = json.loads(user.meta_data)
                user.meta_data['profile_picture'] = filename
                user.meta_data = json.dumps(user.meta_data)
                session.commit()

            return redirect(url_for('user.profile'), code=302)

    except Exception as exc:
        log_api_error(logger, exc, request)
        return redirect(url_for('main.index'), code=302)
# end: USER


# start: AUTH
@api.route('/login-user', methods=['POST'])
def login_user_profile():
    try:
        with database_manager as session:
            user = session.query(database_manager.User).filter_by(username=request.form.get("username")).first()

            if user and user.password == request.form.get("password"):
                login_user(user, remember=bool(request.form.get('remember')))

                user.meta_data = json.loads(user.meta_data)
                user.meta_data.update({
                    'last_login_datetime': str(dt.datetime.now()),
                    'last_login_user_info': {
                        'remote_addr': request.remote_addr,
                        'x_forwarded_for': request.headers.get('X-Forwarded-For')
                    }
                })
                user.meta_data = json.dumps(user.meta_data)
                session.commit()

                flash('You were successfully logged in')
                return redirect(url_for('admin.index'))
            else:
                flash('Wrong username or password.', 'error')
                return redirect(url_for('auth.login'))
    except Exception as exc:
        log_api_error(logger, exc, request)
        return redirect(url_for('admin.index'), code=302)

@api.route('/signup-user', methods=['POST'])
@login_required
def signup_user():
    try:
        with database_manager as session:
            user = session.query(database_manager.User).filter_by(username=request.form.get('username')).first()

        if user:
            return redirect(url_for('auth.login'))
        else:
            with database_manager as session:
                new_user = database_manager.User(
                    id=generate_id('uuid'),
                    username=request.form.get('username'),
                    password=request.form.get('password'),
                    meta_data=json.dumps({'email': request.form.get('email'), "is_admin": "False", "is_employee": "False" }))

                session.add(new_user)
                # session.commit()

            return redirect(url_for('auth.login'))

    except Exception as exc:
        log_api_error(logger, exc, request)
        return redirect(url_for('admin.index'), code=302)

@api.route('alter-user-password/<string:user_id>', methods=['POST'])
@login_required
def alter_user_password(user_id):
    try:
        with database_manager as session:
            user = session.query(database_manager.User).filter_by(id=user_id).first()

            current_password = request.form['current_password']
            new_password = request.form['new_password']
            new_password_2 = request.form['new_password_2']

            if current_password != user.password:
                flash('Incorrect password', 'error')
            elif new_password != new_password_2:
                flash('New passwords don\'t match', 'error')
            elif len(new_password) <= 4:
                flash('Password length has to be greater than 4.', 'error')
            elif current_password == new_password:
                flash('New password cannot be the same as the current one.', 'error')
            else:
                user.password = new_password
                session.commit()
                flash('Password has successfully been changed')
                return redirect(url_for('user.profile'), code=302)

            return redirect(url_for('auth.reset_password'), code=302)

    except Exception as exc:
        log_api_error(logger, exc, request)
        return redirect(url_for('user.profile'), code=302)
# end: AUTH


# start: SETTINGS
@api.route('/update-currency-conversions', methods=['POST'])
@login_required
def update_currency_conversions():
    with database_manager as session:
        setting = session.query(database_manager.Setting).filter_by(name='currency-conversion').first()
        if setting:
            if setting.last_updated < dt.datetime.now() - dt.timedelta(minutes=4):
                setting.last_updated = dt.datetime.now()
                setting.meta_data = json.loads(setting.meta_data)
                setting.meta_data['eth_to_usd'] = get_eth_to_usd_rate()
                setting.meta_data = json.dumps(setting.meta_data)
                session.commit()
        else:
            new_setting = database_manager.Setting(
                id=generate_id('uuid'), 
                name='currency-conversion', 
                last_updated=dt.datetime.now(), 
                meta_data=json.dumps({'eth_to_usd': get_eth_to_usd_rate()})
            )

            session.add(new_setting)
            session.commit()

    return redirect(url_for('admin.index'), code=302)

@api.route('/delete-file/<string:file_name>', methods=['POST'])
@login_required
def delete_file(file_name):
    try:
        os.remove(os.path.join(config.FILE_UPLOAD_DIR, file_name))
        flash(f'{file_name} deleted successfully')
        return redirect(url_for('admin.index'), code=302)

    except Exception as exc:
        log_api_error(logger, exc, request)
        return redirect(url_for('admin.index'), code=302)
# end: SETTINGS