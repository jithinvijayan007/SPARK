
import os

from skilling_pathway.models import Base
from flask import Flask, json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
if __name__ == "__main__":
    connection_string = (
       os.environ['DATABASE_URL']
    )

    if not database_exists(connection_string):
        create_database(connection_string)

    engine = create_engine(connection_string, echo=True, convert_unicode=True,
    json_serializer=json.dumps)

    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine, checkfirst=True)
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)


