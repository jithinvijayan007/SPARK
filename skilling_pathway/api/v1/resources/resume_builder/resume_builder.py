from http.client import HTTPException
import json
import math
import copy
from io import BytesIO
from flask import send_file,request
import os
from sqlite3 import ProgrammingError
from urllib.error import HTTPError
from sqlalchemy import func
from skilling_pathway.db_session import session
import requests
from . schema import insert_resume_data, get_resume_details
from skilling_pathway.api.v1.decorators import authenticate
from .parser_helper import (
    resume_builder_parser,
    resume_parser,
    resume_filter_parser,    
)
from pyresparser import ResumeParser
from skilling_pathway.api.v1.resources.Resource import API_Resource, NameSpace
api = NameSpace('ResumeBuilder')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
RESUME_DIR = os.path.join(os.path.join(BASE_DIR,'static'),'resumes')

class ResumeBuilderAPI(API_Resource):
    # @authenticate
    @api.expect(resume_builder_parser)
    def post(self):
        try:
            data = resume_builder_parser.parse_args()
            user_resume =  insert_resume_data(data)
            return user_resume
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
    
    @api.expect(resume_filter_parser)
    def get(self):
        try:
            data = resume_filter_parser.parse_args()
            resume_details = get_resume_details(data)
            
            return {
                "message": "Resume Created succefully",
                "status": True,
                "data": resume_details
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

def resume_parser(path):
    data = ResumeParser(path).get_extracted_data()
    return data

class UploadResume(API_Resource):
    @api.expect(resume_parser)
    def post(self):
        try:
            resume_file = request.files['resume']
             #This prints the file name of the uploaded file
            print(resume_file.filename)
            resume_path = os.path.join(RESUME_DIR,resume_file.filename)
            resume_file.save(resume_path)
            json_data = resume_parser(resume_path)
            
            if os.path.exists(resume_path):
                os.remove(resume_path)
            
            return {
                "message": "Resume Created succefully",
                "status": True,
                "data": json_data
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
        