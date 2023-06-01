from datetime import datetime
from flask_restx import reqparse
import werkzeug

course_grant_parser = reqparse.RequestParser()
course_grant_parser.add_argument(
    "participant_id", type=str, required=True
)
course_grant_parser.add_argument(
    "course_name", type=str, required=True
)
course_grant_parser.add_argument(
    "course_id", type=int, required=True
)
course_grant_parser.add_argument(
    "funder_id", type=str, required=False
)
course_grant_parser.add_argument(
    "course_actual_price", type=str, required=False
)
course_grant_parser.add_argument(
    "course_offer_price", type=str, required=False
)


course_grant_check_parser = reqparse.RequestParser()
course_grant_check_parser.add_argument(
    "participant_id", type=str, required=True
)
course_grant_check_parser.add_argument(
    "course_id", type=int, required=True
)



user_post_parser = reqparse.RequestParser()
user_post_parser.add_argument("user_name", type=str, required=True, help="User Name is required")
user_post_parser.add_argument("email", type=str, required=True, help="Email is required")
user_post_parser.add_argument("password", type=str, required=True, help="Password is required")
user_post_parser.add_argument("first_name", type=str, required=True, help="First Name is required")
user_post_parser.add_argument("last_name", type=str, required=False)
user_post_parser.add_argument("role", type=str, required=True, choices=('admin','merchant','customer'),help="role is required")

user_login_parser = reqparse.RequestParser()
user_login_parser.add_argument("email", type=str, required=True, location="json", help="Email is required")
user_login_parser.add_argument("password", type=str, required=True, location="json", help="Password is required")

me_get_parser = reqparse.RequestParser()
me_get_parser.add_argument("access-token", type=str, required=True, location="headers", help="access-token is required")

store_post_parser = reqparse.RequestParser()
store_post_parser.add_argument(
    "store_name", type=str, required=True, location='form', help="Store Name is required"
)
store_post_parser.add_argument(
    "store_address", type=str, required=True, location='form', help="Store Address is required"
)
store_post_parser.add_argument(
    "store_city", type=str, required=True, location='form', help="Store City is required"
)
store_post_parser.add_argument(
    "image", type=str, required=False, location='files'
)

store_get_parser = reqparse.RequestParser()
store_get_parser.add_argument(
    "store_name", type=str, required=False
)

user_put_parser = reqparse.RequestParser()
user_put_parser.add_argument("email", type=str, required=False)
user_put_parser.add_argument("first_name", type=str, required=False)
user_put_parser.add_argument("last_name", type=str, required=False)

store_put_parser = reqparse.RequestParser()
store_put_parser.add_argument("store_name", type=str, required=False)
store_put_parser.add_argument("store_address", type=str, required=False)
store_put_parser.add_argument("store_city", type=str, required=False)