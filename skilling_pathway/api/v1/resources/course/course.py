from http.client import HTTPException
import json
import math
import copy
from io import BytesIO
from flask import send_file
import os
from sqlite3 import ProgrammingError
from urllib.error import HTTPError
from sqlalchemy import func
from skilling_pathway.db_session import session
import requests
from skilling_pathway.api.v1.decorators import authenticate
from .parser_helper import (
    course_list_parser,
    course_by_id_parser
)

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

            url = "https://lms.samhita.org//webservice/rest/server.php?wstoken=9b90383be92709097c2edb05a1dfa7b5&wsfunction=core_course_get_courses&moodlewsrestformat=json"

            payload={}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)
            result = response.json()


            return {
                "message": "Courses fetched succefully",
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
        

class CourseByID(API_Resource):
    @authenticate
    @api.expect(course_by_id_parser)
    def get(self, id):
        try:
            url = f"https://lms.samhita.org//webservice/rest/server.php?wstoken=9b90383be92709097c2edb05a1dfa7b5&wsfunction=core_course_get_courses&moodlewsrestformat=json&options[ids][0]={id}"

            payload={}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)


            result = response.json()


            return {
                "message": "Courses details succefully",
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