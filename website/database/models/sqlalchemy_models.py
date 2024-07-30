from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, String, Integer, Float, MetaData, DateTime, Text)

from flask_login import UserMixin

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class Setting(Base):
    __tablename__ = 'settings'
    id = Column(String, primary_key=True)
    name = Column(String(100), unique=True)
    last_updated = Column(DateTime)
    meta_data = Column(Text)


class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    username = Column(String(100), unique=True)
    password = Column(String(100))
    meta_data = Column(Text)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(String, primary_key=True, unique=True)
    date = Column(DateTime)
    amount = Column(Float)
    category = Column(String)
    notes = Column(String)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    type = Column(String)