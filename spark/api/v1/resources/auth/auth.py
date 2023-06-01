import os
from datetime import timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from spark.db_session import session
from spark.api.v1.json_encoder import AlchemyEncoder
from .parser_helper import (
    user_post_parser,
    user_login_parser,
    store_post_parser,
    store_get_parser,
    user_put_parser,
    store_put_parser
)
from .schema import *
from spark.api.v1.resources.Resource import API_Resource, NameSpace
from spark.models.auth.auth import *

api = NameSpace('Course')
      

class RegisterApi(API_Resource):
    @api.expect(user_post_parser)
    def post(self):
        try:
            data = user_post_parser.parse_args()
            user_name = data["user_name"]
            email = data["email"],
            role = data["role"]
            password = data["password"]
            first_name = data["first_name"]
            last_name = data["last_name"]

            # check if email already exists
            user = bool(session.query(User).filter(User.email==email).first())
            if user:
                return {"message": "Email already exists"}, 400
            
            # check if usename already exists
            user = bool(session.query(User).filter(User.username==user_name).first())
            if user:
                return {"message": "Username already exists"}, 400
            
            if not user_name.isalnum() or " " in user_name:
                return {'error': "Username should be alphanumeric, also no spaces"}, 400
            
            # if not validators.email(email):
            #     return {'error': "Email is not valid"}, 400

            # create new user
            pwd_hash = generate_password_hash(password)
            user = User(email=email, username=user_name, password=pwd_hash, role=role, 
                        first_name=first_name, last_name=last_name)
            session.add(user)
            session.commit()

            user_id = user.id
            return {"message": "User created successfully", "user_id": str(user_id)}, 201
        except Exception as e:
            session.rollback()
            session.commit()
            return {"message": f"Something went wrong -- {str(e)}"}, 500


class LoginApi(API_Resource):
    @api.expect(user_login_parser)
    def post(self):
        try:
            data = user_login_parser.parse_args()
            email = data["email"]
            password = data["password"]

            # check if email exists
            user = session.query(User).filter(User.email==email).first()
            if not user:
                return {"message": "Email does not exist"}, 400

            # check if password is correct
            is_pass_correct = check_password_hash(user.password, password)

            if is_pass_correct:

                expires = timedelta(days=1)
                # Generate the access token
                access_token = create_access_token(identity=user.id, expires_delta=expires)
                
                # Generate the refresh token
                refresh = create_refresh_token(identity=user.id)

                return {'refresh': refresh,
                        'access': access_token,
                        'username': user.username,
                        'email': user.email}, 200
            return {'error': 'Wrong credentials'}, 401
            
        except Exception as e:
            session.rollback()
            session.commit()
            return {"message": f"Something went wrong -- {str(e)}"}, 500

        
class StoreAPI(API_Resource):
    @api.expect(store_post_parser)
    @jwt_required
    def post(self):
        try:
            data = store_post_parser.parse_args()
            user_id = get_jwt_identity()
            user = session.query(User).filter(User.id==user_id).first()
            #check role
            if user.role == "customer":
                return {"message": "You are not authorized to create store"}, 401
            
            store_name = data["store_name"]
            store_address = data["store_address"]
            store_city = data["store_city"]
            image = data["image"]
            if image:

                #upload image to s3
                output = upload_file_to_s3(profile_image)
                if output:
                    bucket= os.getenv("AWS_S3_BUCKET_NAME")
                    BASE_URL = 'uploads/'
                    profile_image = f'https://{bucket}.s3.amazonaws.com/{BASE_URL}{profile_image.filename}'
                    
            #create store
            store = Store(store_name=store_name, store_address=store_address,
                          store_city=store_city, created_by=user_id, image=profile_image)
            session.add(store)
            session.commit()
            return {"message": "Store created successfully"}, 201
        
        except Exception as e:
            session.rollback()
            session.commit()
            return {"message": f"Something went wrong -- {str(e)}"}, 500
        
    @api.expect(store_get_parser)
    @jwt_required
    def get(self):
        try:
            data = store_get_parser.parse_args()
            user_id = get_jwt_identity()
            #get the user
            user = session.query(User).filter(User.id==user_id).first()
            if user.role in ["customer","admin"]:
                store = session.query(Store).filter(Store.is_active==True).all()                
            store = session.query(Store).filter(and_(Store.created_by==user_id, Store.is_active==True)).all()
            if not store:
                return {"message": "Store does not exist"}, 400
            serialized_entries = json.loads(
                json.dumps(store, cls=AlchemyEncoder)
            )
            return {"message": "Store retrieved successfully", "store": serialized_entries}, 200
        except Exception as e:
            session.rollback()
            session.commit()
            return {"message": f"Something went wrong -- {str(e)}"}, 500    
        

class StoreEditAPI(API_Resource):
    @api.expect(store_put_parser)
    @jwt_required
    def put(self, id):
        try:
            data = store_put_parser.parse_args()
            user_id = get_jwt_identity()
            store_name = data["store_name"]
            store_address = data["store_address"]
            store_city = data["store_city"]
            
            #check if user exists
            store = session.query(Store).filter(and_(Store.id==id,Store.is_active==True)).first()
            if not store:
                return {"message": "Shop does not exist"}, 400
            
            #check user permission, only customer can edit profile
            if store.created_by != user_id:
                return {"message": "You are not authorized to edit this store"}, 401

            #update store
            store.store_name = store_name   
            store.store_address = store_address
            store.store_city = store_city
            session.commit()
            return {"message": "Store Updated successfully"}, 200

        except Exception as e:
            session.rollback()
            session.commit()
            return {"message": f"Something went wrong -- {str(e)}"}, 500
        

    @jwt_required
    def delete(self, id):
        try:
            user_id = get_jwt_identity()
            
            #check if user exists
            store = session.query(Store).filter(Store.id==id).first()
            if not store:
                return {"message": "Shop does not exist"}, 400
            
            #check user permission, only customer can edit profile
            if store.created_by != user_id:
                return {"message": "You are not authorized to delete this store"}, 401

            #update store
            store.is_active = False   
            session.commit()
            return {"message": "Store Deleted successfully"}, 200

        except Exception as e:
            session.rollback()
            session.commit()
            return {"message": f"Something went wrong -- {str(e)}"}, 500
        

class ProfileEditAPI(API_Resource):
    @api.expect(user_put_parser)
    @jwt_required
    def put(self, id):
        try:
            data = user_put_parser.parse_args()
            user_id = get_jwt_identity()
            email = data["email"]
            first_name = data["first_name"]
            last_name = data["last_name"]

            #check user permission, only customer can edit profile
            loged_in_user = session.query(User).filter(User.id==user_id).first()
            if loged_in_user.role != "customer":
                return {"message": "You are not authorized to edit user"}, 401
            
            #check if user exists
            user = session.query(User).filter(User.id==id).first()
            if not user:
                return {"message": "User does not exist"}, 400

            if user.email != email:
                # check if email already exists
                exist = bool(session.query(User).filter(User.email==email).first())
                if exist:
                    return {"message": "Email already exists"}, 400
            
            
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            session.commit()
            return {"message": "User Updated successfully", "user_id": str(user_id)}, 200
        except Exception as e:
            session.rollback()
            session.commit()
            return {"message": f"Something went wrong -- {str(e)}"}, 500
        
    




