from .config import *

def check_dirs():
    directories = [ROOT_DIR, DATABASE_DIR, LOG_DIR, FILE_UPLOAD_DIR]
    files = [DATABASE, SERVICE_LOG, DATABASE_LOG, ENV_FILE]

    for item in directories + files:
        if not os.path.exists(item):
            if item in directories:
                os.mkdir(item)
            else:
                open(item, 'a').close()

check_dirs()

