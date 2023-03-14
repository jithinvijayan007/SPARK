from flask import Blueprint
from flask_restx import Api


v2_blueprint = Blueprint(name="v2", import_name=__name__)
v2_api = Api(app=v2_blueprint, prefix="/v2",doc='/v2/apidocs/')