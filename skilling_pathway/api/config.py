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

config = Config()