from http.client import HTTPException
import json
import math
import copy
from io import BytesIO
from flask import request, current_app, send_file
import os
from sqlite3 import ProgrammingError
from urllib.error import HTTPError
from sqlalchemy import func
from skilling_pathway.db_session import session
import requests
from skilling_pathway.api.v1.json_encoder import AlchemyEncoder
from skilling_pathway.api.v1.decorators import authenticate
from .parser_helper import (
    course_list_parser,
    course_by_id_parser,
    course_content_parser,
    course_grant_parser,
    course_grant_dashboard_parser,
    course_grant_dashboard_get_parser
)
from .schema import *

# from .course import (
#    InstitutionMaster,
#    CourseCategory,
#    CourseMaster,
#    CourseModuleMaster,
#    ModuleContentMaster
# )
from skilling_pathway.api.v1.resources.Resource import API_Resource, NameSpace
api = NameSpace('Course')
class CourseList(API_Resource):
    @authenticate
    @api.expect(course_list_parser)
    def get(self):
        try:

            url = "https://dev.lms.samhita.org//webservice/rest/server.php?wstoken=9b90383be92709097c2edb05a1dfa7b5&wsfunction=core_course_get_courses&moodlewsrestformat=json"

            payload={}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code in (range(200,299)):
                result = response.json()
                return {
                "message": "Courses fetched succefully",
                "status": True,
                "data": result
                }, 200
            else:
                return {
                "message": response.reason,
                "status": False,
                "data": response.reason
                }, response.status_code            


        except Exception as e:
            import traceback
            print(e)
            session.rollback()
            session.commit()
            return {
                "message": str(traceback.format_exc()),
                "status": False,
                "type": "custom_error"
            }, 400
        

class CourseByID(API_Resource):
    @authenticate
    @api.expect(course_by_id_parser)
    def get(self, id):
        try:
            url = f"https://dev.lms.samhita.org//webservice/rest/server.php?wstoken=9b90383be92709097c2edb05a1dfa7b5&wsfunction=core_course_get_courses&moodlewsrestformat=json&options[ids][0]={id}"

            payload={}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)


            result = response.json()


            return {
                "message": "Courses details fetched succefully",
                "status": True,
                "data": result
            }, 200


        except Exception as e:
            import traceback
            print(e)
            session.rollback()
            session.commit()
            return {
                "message": str(traceback.format_exc()),
                "status": False,
                "type": "custom_error"
            }, 400
        
class CourseListNew(API_Resource):
    @authenticate
    @api.expect(course_list_parser)
    def get(self):
        try:

            url = "https://dev.lms.samhita.org//webservice/rest/server.php?wstoken=9b90383be92709097c2edb05a1dfa7b5&wsfunction=core_course_get_courses_by_field&moodlewsrestformat=json"

            payload={}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code in (range(200,299)):
                result = response.json()
                return {
                "message": "Courses fetched succefully",
                "status": True,
                "data": result
                }, 200
            else:
                return {
                "message": response.reason,
                "status": False,
                "data": response.reason
                }, response.status_code            


        except Exception as e:
            import traceback
            print(e)
            session.rollback()
            session.commit()
            return {
                "message": str(traceback.format_exc()),
                "status": False,
                "type": "custom_error"
            }, 400
        

class CourseContentAPI(API_Resource):
    @authenticate
    @api.expect(course_content_parser)
    def get(self, id):
        try:
            url = f"https://dev.lms.samhita.org//webservice/rest/server.php?wstoken=9b90383be92709097c2edb05a1dfa7b5&wsfunction=core_course_get_contents&moodlewsrestformat=json&courseid={id}"

            payload={}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)


            result = response.json()


            return {
                "message": "Courses details fetched succefully",
                "status": True,
                "data": result
            }, 200


        except Exception as e:
            import traceback
            print(e)
            session.rollback()
            session.commit()
            return {
                "message": str(traceback.format_exc()),
                "status": False,
                "type": "custom_error"
            }, 400
        

class CourseGrantAPI(API_Resource):
    @authenticate
    @api.expect(course_grant_parser)
    def post(self):
        try:
            data = course_grant_parser.parse_args()
            user = request.user
            resp = course_grant_create(data,user)
            return resp


        except Exception as e:
            import traceback
            print(e)
            session.rollback()
            session.commit()
            return {
                "message": str(traceback.format_exc()),
                "status": False,
                "type": "custom_error"
            }, 400
        


class CourseGrantDashboardAPI(API_Resource):
    @authenticate
    @api.expect(course_grant_dashboard_parser)
    def post(self):
        try:
            data = course_grant_dashboard_parser.parse_args()
            resp = course_grant_status_update(data)
            return resp


        except Exception as e:
            import traceback
            print(e)
            session.rollback()
            session.commit()
            return {
                "message": str(traceback.format_exc()),
                "status": False,
                "type": "custom_error"
            }, 400
        
    @authenticate
    @api.expect(course_grant_dashboard_get_parser)
    def get(self):
        try:
            grants = session.query(CourseGrantMaster).all()
            serialized_entries = json.loads(
                json.dumps(grants, cls=AlchemyEncoder)
            )
            return {
                'status': True,
                'message': 'Grant status updated successfully',
                'type': 'success',
                'data': serialized_entries
                }, 200


        except Exception as e:
            import traceback
            print(e)
            session.rollback()
            session.commit()
            return {
                "message": str(traceback.format_exc()),
                "status": False,
                "type": "custom_error"
            }, 400
        


