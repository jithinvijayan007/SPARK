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
from skilling_pathway.models.profile import *
from skilling_pathway.models.course import *

def profile_resume_update(data,id):
    try:
        import pdb;pdb.set_trace()
        prof = session.query(ParticipantProfile).filter(ParticipantProfile.id==id).first()
        if prof:
            if data.get('current_skills'):
                current_skills = data.get('current_skills').split(',')
                new_list = prof.current_skills
                new_list.extend(current_skills)
                prof.current_skills=new_list
            if data.get('other_languages'):
                current_skills = data.get('other_languages').split(',')
                new_list = prof.current_skills
                new_list.extend(current_skills)
                prof.other_languages = new_list
            if data.get("interested_course"):
                current_skills = data.get('interested_course').split(',')
                new_list = prof.current_skills
                new_list.extend(current_skills)
                prof.interested_course = new_list
            if data.get("educational_qualifications"):
                current_skills = data.get('educational_qualifications').split(',')
                new_list = prof.current_skills
                new_list.extend(current_skills)
                prof.educational_qualifications = new_list
            prof.address=data.get('address')
            prof.email=data.get('email')
            prof.mobile=data.get('mobile')
            prof.gender=data.get('gender')
            session.commit()
            return {
                    "message": "Profile updated succefully",
                    "status": True,
                    "data": {}
                }, 200

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
