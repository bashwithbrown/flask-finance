from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .models import *


class DatabaseManager(object):
    def __init__(self, databaseFile):
        self.engine = create_engine(
            f"sqlite:///{databaseFile}",
            connect_args={'check_same_thread': False}
        )

        self.Transaction = Transaction
        self.Category = Category
        self.Setting = Setting
        self.User = User
        self.create_models()

    def __enter__(self):
        session_factory = sessionmaker(bind=self.engine)
        session = scoped_session(session_factory)
        self.session = session()
        return self.session

    def __exit__(self, ext_type, exc_value, traceback):
        self.session.close()
        if isinstance(exc_value, Exception):
            self.session.rollback()
            print(f"DATABASE ERROR OCCURRED: {exc_value} ROLLING BACK CHANGES")
        else:
            self.session.commit()
        self.session.close()

    def create_models(self):
        Base.metadata.create_all(self.engine)

