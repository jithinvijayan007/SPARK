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
