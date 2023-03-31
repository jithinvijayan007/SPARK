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

# from .course import (
#    InstitutionMaster,
#    CourseCategory,
#    CourseMaster,
#    CourseModuleMaster,
#    ModuleContentMaster
# )
from skilling_pathway.api.v1.resources.Resource import API_Resource, NameSpace
class CourseList(API_Resource):
    # @authenticate
    # @api.expect(unfilled_forms_get_parser)
    def get(self):
        try:

            url = "https://lms.samhita.org//webservice/rest/server.php?wstoken=9b90383be92709097c2edb05a1dfa7b5&wsfunction=core_course_get_courses&moodlewsrestformat=json"

            payload={}
            headers = {
            'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            'Pragma': 'no-cache',
            'sec-ch-ua-platform': '"macOS"',
            'sec-ch-ua-mobile': '?0',
            'access-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4MDI2MTEyNiwianRpIjoiOTQxMTc2NjUtZWZjZC00MTYwLWJmNDgtOTI1YmM0NTY3MWM5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjBkYzM2M2UxLThhZmUtNDcxMS05OGRmLTBjOWI3ZmIwZDliMyIsIm5iZiI6MTY4MDI2MTEyNiwiZXhwIjoxNjgwMzQ3NTI2fQ.II4AEJ_pfXClo7lvvThW9Ig7RBU687WXQ4AE7-3NK94',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, /',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Referer': 'http://localhost:5400/',
            'Expires': '0'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            print(response.text)
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
    # @authenticate
    # @api.expect(unfilled_forms_get_parser)
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