import json
import time
import datetime as dt

from flask import (Flask, render_template, request, url_for, redirect, jsonify, flash, Blueprint)
from flask_login import login_required, current_user

from core import config
from database import DatabaseManager
from functions import Logger, retreive_transactions_from_db, kraken_request, get_ethereum_balance, get_ethereum_transactions, wei_to_ether 

main = Blueprint('main', __name__, static_folder='../static/', template_folder='../templates/main')
logger = Logger(config)
database_manager = DatabaseManager(config.DATABASE)

@main.route('/', methods=['GET'])
@login_required
def index():
    return redirect(url_for('main.home'))

@main.route('/home', methods=['GET'])
@login_required
def home():
    config.INSTANCE_META_DATA['timeline'] = request.args.get('timeline', 'ytd')

    crypto_data = {}
    meta_data = json.loads(current_user.meta_data)
    
    kraken_data = kraken_request('/0/private/Balance', {"nonce": str(int(1000*time.time()))}, meta_data['kraken_api_key'], meta_data['kraken_api_secret']).json()
    if kraken_data:
        crypto_data['kraken_balance'] =  kraken_data['result']

    with database_manager as session:
        eth_to_usd_rate = json.loads(session.query(database_manager.Setting).filter_by(name='currency-conversion').first().meta_data)['eth_to_usd']

    crypto_data['eth_balance'] =  wei_to_ether(get_ethereum_balance(meta_data['etherscan_api_key'], meta_data['ethereum_wallet_address'])) * eth_to_usd_rate
    crypto_data['eth_address'] =  meta_data['ethereum_wallet_address']

    return render_template('home.html', metrics=retreive_transactions_from_db(database_manager)[1], meta_data=config.INSTANCE_META_DATA, crypto=crypto_data)


