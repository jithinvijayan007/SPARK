# Python Imports
import os

# SQL Alchemy Imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from config import SQLALCHEMY_DATABASE_URI
# an Engine, which the Session will use for connection
# resources
engine = create_engine(os.environ['DATABASE_URL'])

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
