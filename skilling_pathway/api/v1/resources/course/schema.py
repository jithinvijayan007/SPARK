from http.client import HTTPException
import json
import math
import copy
from sqlalchemy import or_, and_
from io import BytesIO
from flask import request, current_app, send_file
import os
from sqlite3 import ProgrammingError
from urllib.error import HTTPError
from sqlalchemy import func
from skilling_pathway.db_session import session
import requests
from skilling_pathway.models.course import *


def course_grant_create(data,user):
    try:
        grant = session.query(CourseGrantMaster).filter(and_(CourseGrantMaster.participant_id==data.get('participant_id')),\
                            CourseGrantMaster.course_id==data.get('course_id')).first()
        if grant:
            return {
                "message": "Allready requested for the same course",
                "status": False,
                "data": {}
            }, 400

        course_grant=CourseGrantMaster(
                    participant_id=data.get("participant_id"),
                    course_name=data.get("course_name"),
                    course_id=data.get("course_id"),
                    funder_id=data.get("funder_id"),
                    course_actual_price=data.get("course_actual_price"),
                    course_offer_price=data.get("course_offer_price"),
                    created_by=user,
                    status='requested'
                )
        session.add(course_grant)
        session.commit()
        return {
                "message": "Requested for course grant succefully",
                "status": True,
                "data": {}
            }, 200

    except Exception as e:
        session.rollback()
        session.commit()
        print("validation error",e)
        raise ValueError(str(e.args))
    
def course_grant_check(data):
    try:
        grant = session.query(CourseGrantMaster).filter(and_(CourseGrantMaster.participant_id==data.get('participant_id'),\
                                                    CourseGrantMaster.course_id==data.get('course_id'))).first()
        if grant:
            return {'exist':True}
        return {'exist':False}
    except Exception as e:
        session.rollback()
        session.commit()
        print("validation error",e)
        raise ValueError(str(e.args))

    
def course_grant_status_update(data):
    try:
        id = data.get('id')
        grant = session.query(CourseGrantMaster).filter(CourseGrantMaster.id==id).first()
        if grant:
            grant.status = data.get('status')
            session.commit()
            return {
                'status': True,
                'message': 'Grant status updated successfully',
                'type': 'success'
                }, 200
        return {
                "message": "Grant doesn't exist",
                "status": False,
                "type": "custom_error"
            }, 400

    except Exception as e:
        session.rollback()
        session.commit()
        print("validation error",e)
        raise ValueError(str(e.args))
    
    
MOODLE_BASE_URL = os.environ.get("MOODLE_BASE_URL")
MOODLE_ADMIN_TOKEN = os.environ.get("MOODLE_ADMIN_TOKEN")
MOODLE_USER_LIST_FN = os.environ.get("MOODLE_USER_LIST_FN")
MOODLE_COURSE_LIST_FN = os.environ.get("MOODLE_COURSE_LIST_FN")

def course_status(course_id,access_token,request_data):
    user_details,is_exist = isUserExist(request_data['user_name'],request_data['user_name'])
    if is_exist:
        user_id = user_details[0]['id']
        url = f"{MOODLE_BASE_URL}?wstoken={MOODLE_ADMIN_TOKEN}&wsfunction=core_completion_get_course_completion_status&moodlewsrestformat=json"

        payload={
                'userid':user_id,
                'courseid':course_id
            }
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        json_response = response.json()
        if json_response.get('completionstatus'):
            # completions = json_response.get('completionstatus')
            # completion = completions.get('completions')
            # length = len(completion)
            # completed = 0
            # for i in completion:
            #     if i.get('complete')  == True:
            #         completed += 1
            # percentage = (completed / length) * 100
            # json_response['completionstatus']['percentage']=percentage
            return json_response,response.status_code
        
        return response.json(),response.status_code
    
def isUserExist(email,username):
    fields = {'email':email,'username':username}
    for field,value in fields.items():
        url = f"{MOODLE_BASE_URL}?wstoken={MOODLE_ADMIN_TOKEN}&wsfunction={MOODLE_USER_LIST_FN}&field={field}&values[0]={value}&moodlewsrestformat=json"
        payload={}
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if len(response.json()):
            return response.json(), True
    return '',False
