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
from . schema import insert_resume_data
from skilling_pathway.api.v1.decorators import authenticate
from .parser_helper import (
    resume_builder_parser,
    resume_parser,
    resume_filter_parser,    
)
from pyresparser import ResumeParser
from skilling_pathway.api.v1.resources.Resource import API_Resource, NameSpace
api = NameSpace('ResumeBuilder')


class ResumeBuilder(API_Resource):
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
            users = session.query(ResumeBuilder).filter(ResumeBuilder.id !=data.get('id')).\
                    order_by(ResumeBuilder.created_at.desc())
            import pdb;pdb.set_trace()
            
            return {
                "message": "Resume Created succefully",
                "status": True,
                "data": []
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

def show_data(data):
    path = 'https://s3revive.s3.amazonaws.com/uploads/aaa.pdf'
    data = ResumeParser(path).get_extracted_data()
    return data

class UploadResume(API_Resource):
    @api.expect(resume_parser)
    def post(self):
        try:
            resume_file = request.files['resume']
            import pdb;pdb.set_trace()
             #This prints the file name of the uploaded file
            print(resume_file.filename)
            #I want to save the uploaded file as logo.png. No matter what the uploaded file name was.
            resume_file.save(resume_file.filename)
            #print(show_data(data))
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
        