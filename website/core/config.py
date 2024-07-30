import os
from dotenv import dotenv_values

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

APP_NAME = ROOT_DIR.split("/")[-1]

DATABASE_DIR = os.path.join(ROOT_DIR, "database")
DATABASE = os.path.join(DATABASE_DIR, "database.db")

LOG_DIR = os.path.join(DATABASE_DIR, "logs")
SERVICE_LOG = os.path.join(LOG_DIR, "service.log")
DATABASE_LOG = os.path.join(LOG_DIR, "database.log")

CORE_DIR = os.path.join(ROOT_DIR, 'core')
ENV_FILE = os.path.join(CORE_DIR, '.env')
CREDENTIALS = dict(dotenv_values(ENV_FILE))

INSTANCE_META_DATA = {}

STATIC_DIR = os.path.join(ROOT_DIR, 'static')
FILE_UPLOAD_DIR = os.path.join(STATIC_DIR, 'file_upload')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

DOMAINS = {'localhost': '127.0.0.1', 'LAN': '192.168.0.177', 'LAN_2': '192.168.120.127'}
PORTS = [7000]

