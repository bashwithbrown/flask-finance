import logging
from pythonjsonlogger import jsonlogger
import inspect

class Logger:
    _instance = None

    def __new__(cls, config):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config):
        if self._initialized:
            return

        self.logger = logging.getLogger(config.APP_NAME)
        self.logger.setLevel(logging.DEBUG)

        self.dbLogger = logging.getLogger("sqlalchemy.engine")
        self.dbLogger.setLevel(logging.INFO)

        if not self.logger.handlers:
            file_handler = logging.FileHandler(config.SERVICE_LOG)
            file_handler.setLevel(logging.INFO)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)

            formatter = jsonlogger.JsonFormatter(
                fmt="%(levelname)s %(asctime)s %(module)s %(name)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                json_ensure_ascii=True,
            )

            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        if not self.dbLogger.handlers:
            dbFileHandler = logging.FileHandler(config.DATABASE_LOG)
            dbFileHandler.setLevel(logging.ERROR)
            dbFileHandler.setFormatter(formatter)

            self.dbLogger.addHandler(dbFileHandler)

        self._initialized = True

    def log(self, message, severity="", **kwargs):
        frame = inspect.currentframe().f_back
        function_name = frame.f_code.co_name
        file_name = frame.f_code.co_filename
        line_number = frame.f_lineno

        extra_info = {
            'FuncName': function_name,
            'FileName': file_name.split('/')[-1],
            'LineNo': line_number,
            'meta_data': kwargs.get('meta_data', {})
        }

        if not severity or severity == "info":
            self.logger.info(message, extra=extra_info)
        elif severity == "debug":
            self.logger.debug(message, extra=extra_info)
        elif severity == "warning":
            self.logger.warning(message, extra=extra_info)
        elif severity == "error":
            self.logger.error(message, extra=extra_info)
        elif severity == "critical":
            self.logger.critical(message, extra=extra_info)