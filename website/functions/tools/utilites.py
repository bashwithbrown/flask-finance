import re
import json
import uuid
import math
import random
import string
import bcrypt
import datetime as dt


def generate_id(id_type):
    if id_type == 'uuid':
        return str(uuid.uuid4())

    elif id_type == 'string':
        str1 = "".join((random.choice(string.ascii_letters) for _ in range(5)))
        str1 += "".join((random.choice(string.digits) for _ in range(5)))
        sam_list = list(str1)
        random.shuffle(sam_list)
        random_id = "".join(sam_list)
        return random_id

    elif id_type == 'number':
        return random.randint(1, 100000)
    else:
        return None


def calculate_financial_metrics(transactions):
    total_income = 0.0
    total_expenses = 0.0
    ytd_return = 0.0

    income_by_year = {}
    expenses_by_year = {}

    current_year = dt.datetime.now().year

    for transaction in transactions:

        if transaction.category_type == 'INCOME':
            total_income += transaction.amount

        elif transaction.category_type == 'EXPENSE':
            total_expenses += transaction.amount

        transaction_year = transaction.date.year

        if transaction_year not in income_by_year:
            income_by_year[transaction_year] = 0.0
        if transaction_year not in expenses_by_year:
            expenses_by_year[transaction_year] = 0.0

        if transaction.category_type == 'INCOME':
            income_by_year[transaction_year] += transaction.amount
        elif transaction.category_type == 'EXPENSE':
            expenses_by_year[transaction_year] += transaction.amount

    if current_year in income_by_year and current_year in expenses_by_year:
        ytd_return = income_by_year[current_year] - expenses_by_year[current_year]

    metrics = {
        'total_income': round(total_income, 2),
        'total_expenses': round(total_expenses, 2),
        'total_return': round(total_income - total_expenses, 2),
        'ytd_return': round(ytd_return, 2),
        'income_by_year': income_by_year,
        'expenses_by_year': expenses_by_year
    }

    metrics['total_savings_rate'] = round(metrics['total_return'] / metrics['total_income'] * 100, 2)
    metrics['ytd_income'] = round(metrics['income_by_year'][current_year], 2)
    metrics['ytd_expenses'] = round(metrics['expenses_by_year'][current_year], 2)
    metrics['ytd_savings_rate'] = round(metrics['ytd_return'] / metrics['ytd_income'] * 100, 2)
    return metrics


def calculate_returns(income_and_expenses):
    returns = []
    current_balance = 0

    for item in income_and_expenses:
        current_balance += item
        returns.append(current_balance)

    return returns


def retreive_transactions_from_db(database_manager):
    with database_manager as session:

        transactions = session.query(database_manager.Transaction).all()
        categories = session.query(database_manager.Category).all()


        sorted_transactions = sorted(
            transactions,
            key=lambda transaction: transaction.date,
            reverse=True
        )

        new_transactions = []
        for transaction in sorted_transactions:
            for category in categories:
                if transaction.category == category.name:
                    transaction.category_type = category.type
                    new_transactions.append(transaction)

        metrics = calculate_financial_metrics(new_transactions)

    return new_transactions, metrics
    

def timeHandler(timeSec=0, unit="", strDate="", readable=False, getCurrentTime=False):
    if unit == "s":
        seconds = timeSec
        minutes = seconds // 60
        seconds = seconds % 60
        newTime = {"min": minutes, "sec": seconds}
        return newTime

    if unit == "ms":
        seconds = timeSec / 1000
        minutes = seconds // 60
        newTime = {"min": minutes, "sec": seconds}
        return newTime

    if strDate != "" and readable:
        newTime = f"{dt.datetime.strptime(strDate, '%Y-%m-%d %H:%M:%S'):%b %d %Y %H:%M.%S %p}"
        return newTime

    if getCurrentTime:
        if readable:
            currentTime = f"{dt.datetime.now():%b %d %Y %H:%M.%S %p}"
        else:
            currentTime = dt.datetime.now()

        return currentTime


def validate_user(username, password, database_manager, user_model):
    with database_manager as session:
        user = user_model.query.filter_by(username=username).first()
        if user:
            password_bytes = password.encode("utf-8")
            user_salt = json.loads(user.credentials)['salt']
            new_key = bcrypt.hashpw(password_bytes, user_salt)
            if bcrypt.hashpw(password_bytes, new_key) == user_salt:
                return user
            else:
                return {'msg': 'wrong password or password error'}


def log_api_error(logger, exc, request):
    logger.log(
        message=exc, 
        severity='error', 
        meta_data={
        'method': request.method,
        'path': request.path,
        'remote_addr': request.remote_addr,
        'headers': request.headers
    }) 



def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def object_attributes_to_dict(obj):
    attributes_dict = {}
    for attr_name in dir(obj):
        if not attr_name.startswith('__'):
            if attr_name == 'urls':
                urls_dict = {}
                item = getattr(obj, attr_name)
                for sub_attr_name in dir(item):
                    if not sub_attr_name.startswith('__'):
                        urls_dict[sub_attr_name] = getattr(item, sub_attr_name)

                attributes_dict[attr_name] = urls_dict

            else:
                attributes_dict[attr_name] = getattr(obj, attr_name)

    return attributes_dict


def get_folder_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def convert_file_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])