from http.client import HTTPException
import json
import math
import copy
import time
from io import BytesIO
from flask import send_file,request
import os
from sqlite3 import ProgrammingError
from urllib.error import HTTPError
from sqlalchemy import func
from skilling_pathway.db_session import session
import boto3
from botocore.exceptions import ClientError       
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from trp import Document

import requests
from . schema import insert_resume_data, get_resume_details, allowed_file, upload_file_to_s3, upload_file_to_s3_textract
from skilling_pathway.api.v1.decorators import authenticate
from .parser_helper import (
    resume_builder_parser,
    resume_parser,
    resume_filter_parser,
    comprehend_resume_parser,
    s3_file_upload_parser
)
# from pyresparser import ResumeParser
from skilling_pathway.api.v1.resources.Resource import API_Resource, NameSpace
from pyresparser import ResumeParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
RESUME_DIR = os.path.join(os.path.join(BASE_DIR,'static'),'resumes')

api = NameSpace('ResumeBuilder')


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
class ComprehentResume(API_Resource):
    @api.expect(comprehend_resume_parser)
    def post(self):
        try:
            data = comprehend_resume_parser.parse_args()
            file = data.get('file')
            reader = PdfReader(file)
            page = reader.pages[0]
            text = page.extract_text()
            print(text)
            comprehend = boto3.client(
            service_name='comprehend',
            region_name='ap-south-1',
            aws_access_key_id=os.getenv('AWS_S3_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_S3_SECRET_ACCESS_KEY')
                )
            # output = comprehend.detect_key_phrases(Text=text, LanguageCode='en')
            output = comprehend.detect_entities(Text=text, LanguageCode='en')
            print(output)
            return {
                "message": "Resume Created succefully",
                "status": True,
                "data": output
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
        
 
class TextractResume(API_Resource):
    # @api.expect(resume_parser)
    def post(self):
        try:            
            resume_file = request.files['resume']
             #This prints the file name of the uploaded file
            resume_path = os.path.join(RESUME_DIR,resume_file.filename)
            resume_file.save(resume_path)
            # json_data = resume_parser(resume_path)

            # data = comprehend_resume_parser.parse_args()
            # file = data.get('file')
            # Store Pdf with convert_from_path function
            images = convert_from_path(resume_path)
            if os.path.exists(resume_path):
                os.remove(resume_path)
            
            # for i in range(len(images)):
            
            #     # Save pages as images in the pdf
            #     images[i].save(resume_file.filename + str(i) +'.jpg')
            #     image_file = resume_file.filename + str(i) +'.jpg'
            #     image_path = os.path.join(RESUME_DIR,image_file)
            #     # image_file.save(image_path)
            #     # json_data = resume_parser(image_path)
            #     if image_path and allowed_file(image_file):
            #         output = upload_file_to_s3(image_file)
            #         if output:
            #             bucket= os.getenv("AWS_S3_BUCKET_NAME")
            #             BASE_URL = 'uploads/'
            #             url = f'https://{bucket}.s3.amazonaws.com/{BASE_URL}{file.filename}'
            #             return {'media_url': url},200

            import tempfile
            # import os
            files_name = []
            for i in range(len(images)):
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_image_file:
                    # Save pages as images in the temporary file
                    file_name = temp_image_file.name[5::]
                    images[i].save(file_name)
                    image_path = file_name
                    # json_data = resume_parser(image_path)
                    if image_path and allowed_file(file_name):
                        file = open(file_name,'rb')
                        output = upload_file_to_s3(file)
                        if output:
                            bucket = os.getenv("AWS_S3_BUCKET_NAME")
                            # BASE_URL = 'uploads/'
                            # url = f'https://{bucket}.s3.amazonaws.com/{BASE_URL}{file.name}'
                            files_name.append(output)
            responses = []
            # Amazon Textract client
            textractmodule = boto3.client(service_name='textract',region_name='ap-south-1',
            aws_access_key_id=os.getenv('AWS_S3_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_S3_SECRET_ACCESS_KEY')
                )
            for f in files_name:
                response = textractmodule.analyze_document(
                Document={
                    'S3Object': {
                        'Bucket': os.getenv('AWS_S3_BUCKET_NAME'),
                        'Name': file_name
                    }
                },
                FeatureTypes=["FORMS"])
                doc = Document(response)
                print ('------------- Print Form detected text ------------------------------')
                
                response_dic = {}
                for page in doc.pages:
                    
                    for field in page.form.fields:
                        dic={}
                        resp = ("Key: {}, Value: {}".format(field.key, field.value))
                        dic[str(field.key)] = str(field.value)
                        responses.append(dic)
                for d in responses:
                    for key in d.keys():
                        if 'email' in key.lower():
                            response_dic['email'] = d[key]
                        elif 'skill' in key.lower():
                            response_dic['skills'] = d[key]
                        elif 'education' in key.lower():
                            response_dic['education'] = d[key]
                        elif 'language' in key.lower():
                            response_dic['languages'] = d[key]
                        
                        
            return {'created response':response_dic,
                    'original_response' : responses}
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
        

class TextractPdfResume(API_Resource):
    @api.expect(s3_file_upload_parser)
    def post(self):
        try:  
            data = s3_file_upload_parser.parse_args()
            file = data.get('file')
            url = ''
            if file.filename == '':
                raise FileNotFoundError('No selected file')
            if file and allowed_file(file.filename):
                output = upload_file_to_s3_textract(file)
                if output:
                
                    responses = []
                    # Amazon Textract client
                    textractmodule = boto3.client(service_name='textract',region_name='ap-south-1',
                    aws_access_key_id=os.getenv('AWS_S3_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_S3_SECRET_ACCESS_KEY')
                        )
                    response = textractmodule.analyze_document(
                    Document={
                        'S3Object': {
                            'Bucket': os.getenv('AWS_S3_BUCKET_NAME'),
                            'Name': f"resume/{output}"
                        }
                    },
                    FeatureTypes=["FORMS"])
                    doc = Document(response)
                    print ('------------- Print Form detected text ------------------------------')
                    
                    response_dic = {'email':None,'skills':None,'education':None,'languages':None,'address':None,
                                    'mobile':None,'experience':None,'courses':None,'industry':None,'location':None,
                                    'role':None}
                    for page in doc.pages:
                        
                        for field in page.form.fields:
                            dic={}
                            resp = ("Key: {}, Value: {}".format(field.key, field.value))
                            dic[str(field.key)] = str(field.value)
                            responses.append(dic)
                    for d in responses:
                        for key in d.keys():
                            if 'email' in key.lower():
                                response_dic['email'] = d[key]
                            elif 'skill' in key.lower():
                                response_dic['skills'] = d[key]
                            elif 'education' in key.lower():
                                response_dic['education'] = d[key]
                            elif 'language' in key.lower():
                                response_dic['languages'] = d[key]
                            elif 'dob' in key.lower():
                                response_dic['languages'] = d[key]
                            elif 'address' in key.lower():
                                response_dic['address'] = d[key]
                            elif 'mobile' in key.lower():
                                response_dic['mobile'] = d[key]
                            elif 'experience' in key.lower():
                                response_dic['experience'] = d[key]
                            elif 'course' in key.lower():
                                response_dic['courses'] = d[key]
                            elif 'industry' in key.lower():
                                response_dic['industry'] = d[key]
                            elif 'location' in key.lower():
                                response_dic['location'] = d[key]
                            elif 'role' in key.lower():
                                response_dic['role'] = d[key]
                    return {'created_response':response_dic,
                    'original_response' : responses}


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