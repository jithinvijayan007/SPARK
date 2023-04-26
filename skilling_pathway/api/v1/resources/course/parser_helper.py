from datetime import datetime
from flask_restx import reqparse
import werkzeug

course_list_parser = reqparse.RequestParser()
course_list_parser.add_argument(
    'access-token',type=str,location='headers',required=True,
)

course_by_id_parser = reqparse.RequestParser()
course_by_id_parser.add_argument(
    'access-token',type=str,location='headers',required=True,
)

course_content_parser = reqparse.RequestParser()
course_content_parser.add_argument(
    'access-token',type=str,location='headers',required=True,
)

course_grant_parser = reqparse.RequestParser()
course_grant_parser.add_argument(
    'access-token',type=str,location='headers',required=True,
)
course_grant_parser.add_argument(
    "participant_id", type=str, required=True
)
course_grant_parser.add_argument(
    "course_name", type=int, required=True
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

course_grant_dashboard_parser = reqparse.RequestParser()
course_grant_dashboard_parser.add_argument(
    'access-token',type=str,location='headers',required=True,
)
course_grant_dashboard_parser.add_argument(
    "id", type=str, required=True
)
course_grant_dashboard_parser.add_argument(
    "status", type=str, required=True
)

course_grant_dashboard_get_parser = reqparse.RequestParser()
course_grant_dashboard_get_parser.add_argument(
    'access-token',type=str,location='headers',required=True,
)