import os
import os
from pytz import timezone
from dotenv import load_dotenv

tz = timezone("UTC")
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    # UIM_SECRET_KEY = os.environ.get("UIM_SECRET")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    APP_SETTINGS = os.environ.get("APP_SETTINGS")
    # FLASK_ENV = os.environ.get("FLASK_ENV")
    FLASK_RUN_PORT = os.environ.get("FLASK_RUN_PORT")
    # DRIVE_WEALTH_WRAPPER_URL = os.environ.get("drive_wealth_wrapper_url")
    # UIM_BASE_URL = os.environ.get("UIM_BASE_URL")
    # SERVER_SECRET = os.environ.get("SERVER_SECRET")
    # TEST_DB_URL = os.environ.get("TEST_DB_URL")
    # uim_verify_token_url = UIM_BASE_URL + "/v1/verify/"
    # S3_STATIC_UPLOAD_DIRECTORY = os.environ.get("S3_STATIC_UPLOAD_DIRECTORY")
    # USER_SERVICE_BASE_URL = os.environ.get('USER_SERVICE_BASE_URL')
    # ADMIN_SERVICE_BASE_URL=  os.environ.get("ADMIN_SERVICE_BASE_URL")

config = Config()