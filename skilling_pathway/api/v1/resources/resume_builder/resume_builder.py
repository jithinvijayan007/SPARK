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
    resume_builder_parser,    
)
from skilling_pathway.api.v1.resources.Resource import API_Resource, NameSpace
api = NameSpace('ResumeBuilder')

class ResumeBuilder(API_Resource):
    # @authenticate
    @api.expect(resume_builder_parser)
    def post(self):
        try:
            result = []
            data = resume_builder_parser.parse_args()
            print(data)
            return {
                "message": "Resume Created succefully",
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
    
    def get(self):
        try:
            result = []
            
            return {
                "message": "Resume Created succefully",
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
        