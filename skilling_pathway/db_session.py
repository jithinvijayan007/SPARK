import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from config import SQLALCHEMY_DATABASE_URI
# an Engine, which the Session will use for connection
# resources
engine = create_engine(
    os.environ['DATABASE_URL'], pool_pre_ping=True,
    max_overflow=20, pool_size=10
)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()