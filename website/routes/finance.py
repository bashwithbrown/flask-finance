import json
import datetime as dt
from collections import defaultdict

from flask import (Flask, render_template, request, url_for, redirect, jsonify, flash, Blueprint)
from flask_login import current_user, login_required

from core import config
from database import DatabaseManager
from functions import Logger, retreive_transactions_from_db, get_ethereum_transactions, wei_to_ether

finance = Blueprint('finance', __name__, static_folder='../static/', template_folder='../templates/finance')
logger = Logger(config)
database_manager = DatabaseManager(config.DATABASE)

@finance.route('/', methods=['GET'])
def index():
    return ''


@finance.route('/transactions', methods=['GET'])
def transactions():
    transactions, metrics = retreive_transactions_from_db(database_manager)

    for tx in transactions:
        tx.datetime = tx.date.strftime('%b %d %Y %I:%M.%S %p')

    return render_template('transactions.html', transactions=transactions, metrics=metrics)



@finance.route('/crypto/transactions', methods=['GET'])
def crypto_transactions():
    startblock = 0
    endblock = 99999999
    page = 1
    offset = 10
    sort = 'asc'

    meta_data = json.loads(current_user.meta_data)
    crypto_data = get_ethereum_transactions(meta_data['ethereum_wallet_address'], startblock, endblock, page, offset, sort, meta_data['etherscan_api_key'])

    with database_manager as session:
        eth_to_usd_rate = json.loads(session.query(database_manager.Setting).filter_by(name='currency-conversion').first().meta_data)['eth_to_usd']

    for result in crypto_data['result']:
        ether_balance = wei_to_ether(float(result['value']))
        result['value'] = ether_balance * eth_to_usd_rate


    return render_template('crypto-transactions.html', transactions=crypto_data, crypto_address=meta_data['ethereum_wallet_address'])
    


@finance.route('/transaction-detailed/<tid>', methods=['GET'])
def get_transaction_detailed(tid):
    transaction = [tx for tx in retreive_transactions_from_db(database_manager)[0] if tx.id == tid][0]
    return render_template('transaction-detailed.html', transaction=transaction)


@finance.route('/submit-transaction', methods=['GET'])
def submit_transaction():
    return render_template('submit-transaction.html')


@finance.route('/summary', methods=['GET', 'POST'])
def summary():
    transactions, metrics = retreive_transactions_from_db(database_manager)

    grouped_transactions = {}
    for transaction in transactions:
        year_month_key = (transaction.date.year, transaction.date.month)
        if year_month_key not in grouped_transactions:
            grouped_transactions[year_month_key] = []

        grouped_transactions[year_month_key].append(transaction)

    all_dates = [f"{date[0]}-{date[1]}" for date in grouped_transactions.keys()]

    if request.method == "GET":
        return render_template('summary.html', date_range=all_dates)

    if request.method == "POST":

        date_range = tuple(map(int, request.form['date-range'].split('-')))
        selected_data = grouped_transactions.get(date_range, 0)

        chart_data = defaultdict(float)

        for tx in selected_data:
            chart_data[tx.category] += tx.amount

        new_chart_data = {
            'labels': list(chart_data.keys()),
            'values': list(chart_data.values())
        }

        metrics['montly_income'] = round(sum(transaction.amount for transaction in selected_data if transaction.category_type == "INCOME"), 2)
        metrics['montly_expenses'] = round(sum(transaction.amount for transaction in selected_data if transaction.category_type == "EXPENSE"), 2)

        metrics['montly_balance'] = round(metrics['montly_income'] - metrics['montly_expenses'], 2)
        
        if metrics['montly_income'] != 0:
            metrics['monthly_savings_rate'] = round(metrics['montly_balance'] / metrics['montly_income'] * 100, 2)
        else:
            metrics['monthly_savings_rate'] = 0


        return render_template('summary-detail.html', transactions=selected_data, date_range=all_dates, metrics=metrics, chart_data=new_chart_data)






