from flask_restx import reqparse

profile_create_update_parser = reqparse.RequestParser()
profile_create_update_parser.add_argument(
    "access-token", type=str, required=True, location="headers"
)
profile_create_update_parser.add_argument("participant_id", type=str, location='form', required=True)
profile_create_update_parser.add_argument("form_response", type=str, location='form', required=True)
