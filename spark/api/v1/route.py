from flask import Blueprint
from flask_restx import Api

from spark.api.v1.resources.auth.auth import RegisterApi,LoginApi,StoreAPI,ProfileEditAPI,StoreEditAPI
                                                     

v1_blueprint = Blueprint(name="v1", import_name=__name__)
v1_api = Api(app=v1_blueprint, prefix="/",doc='/apidocs/')

# course api's

v1_api.add_resource(RegisterApi,'/register/')
v1_api.add_resource(LoginApi,'/login/')
v1_api.add_resource(StoreAPI,'/store/')
v1_api.add_resource(StoreEditAPI,'/store/edit/<id>/')
v1_api.add_resource(ProfileEditAPI,'/profile/edit/<id>/')



