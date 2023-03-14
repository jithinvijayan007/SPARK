from flask import Blueprint
from flask_restx import Api

v1_blueprint = Blueprint(name="v1", import_name=__name__)
v1_api = Api(app=v1_blueprint, prefix="/",doc='/apidocs/')