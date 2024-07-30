import json, os
import requests
import datetime as dt

from core import config
from database import DatabaseManager
from functions import convert_file_size

from flask import Blueprint, render_template
from flask_login import login_required


admin = Blueprint('admin', __name__, static_folder='../static/', template_folder='../templates/admin')
database_manager = DatabaseManager(config.DATABASE)


@admin.route('/', methods=['GET'])
@login_required
def index():
    server_files = [
        (file, convert_file_size(os.path.getsize(os.path.join(config.FILE_UPLOAD_DIR, file))), dt.datetime.fromtimestamp(os.stat(os.path.join(config.FILE_UPLOAD_DIR, file)).st_ctime).strftime('%b %d %Y %I:%M.%S %p'))
        for file in os.listdir(config.FILE_UPLOAD_DIR) 
        if os.path.isfile(os.path.join(config.FILE_UPLOAD_DIR, file))
    ]

    logs = []
    with open(config.SERVICE_LOG, 'r') as file:
        content = file.readlines()
        for line in content:
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    data = {
        'server_files_total': len(server_files),
        'log_row_total': len(logs)
    }

    return render_template('admin.html', logs=logs[::-1], server_files=server_files, data=data)

@admin.route('/settings', methods=['GET'])
@login_required
def settings():
    return render_template('settings.html')