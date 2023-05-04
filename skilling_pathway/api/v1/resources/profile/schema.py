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
        prof = session.query(ParticipantProfile).filter(ParticipantProfile.id==id).first()
        if prof:
            # if data.get('current_skills'):
            #     current_skills = data.get('current_skills').split(',')
            #     new_list = prof.current_skills
            #     if new_list:
            #         new_list.extend(current_skills)
            #         prof.current_skills=new_list
            #     else:
            #         prof.current_skills = current_skills
            # if data.get('other_languages'):
            #     current_skills = data.get('other_languages').split(',')
            #     new_list = prof.other_languages
            #     if new_list:
            #         new_list.extend(current_skills)
            #         prof.other_languages = new_list
            #     else:
            #         prof.other_languages = current_skills
            # if data.get("interested_course"):
            #     current_skills = data.get('interested_course').split(',')
            #     new_list = prof.interested_course
            #     if new_list:
            #         new_list.extend(current_skills)
            #         prof.interested_course = new_list
            #     else:
            #         prof.interested_course = current_skills
            # if data.get("educational_qualifications"):
            #     current_skills = data.get('educational_qualifications').split(',')
            #     new_list = prof.educational_qualifications
            #     if new_list:
            #         new_list.extend(current_skills)
            #         prof.educational_qualifications = new_list
            #     else:
            #         prof.educational_qualifications = current_skills
            # if data.get('address'):
            #     prof.address=data.get('address')
            # if data.get('email'):
            #     prof.email=data.get('email')
            # if data.get('mobile'):
            #     prof.mobile=data.get('mobile')
            # if data.get('gender'):
            #     prof.gender=data.get('gender')
            # session.commit()
            if data.get('current_skills'):
                current_skills = data.get('current_skills').split(',')
                new_skill = prof.current_skills
                if new_skill:
                    new_skill.extend(current_skills)
                else:
                    new_skill = current_skills
                new_skill = [*set(new_skill)]
                prof.current_skills=None
            if data.get('other_languages'):
                current_langs = data.get('other_languages').split(',')
                new_langs = prof.other_languages
                if new_langs:
                    new_langs.extend(current_langs)
                else:
                    new_langs = current_langs
                new_langs = [*set(new_langs)]
                prof.other_languages=None
            if data.get("interested_course"):
                current_course= data.get('interested_course').split(',')
                new_course = prof.interested_course
                if new_course:
                    new_course.extend(current_course)
                else:
                    new_course = current_course
                new_course = [*set(new_course)]
                prof.interested_course=None
            if data.get("educational_qualifications"):
                current_qualifi = data.get('educational_qualifications').split(',')
                new_qualifi = prof.educational_qualifications
                if new_qualifi:
                    new_qualifi.extend(current_qualifi)
                else:
                    new_qualifi = current_qualifi
                new_qualifi = [*set(new_qualifi)]
                prof.educational_qualifications=None
            session.commit()

            prof.current_skills=new_skill
            prof.other_languages=new_langs
            prof.interested_course=new_course
            prof.educational_qualifications=new_qualifi
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
        return {
                    "message": "Profile not found ",
                    "status": False,
                    "data": {}
                }, 400

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
