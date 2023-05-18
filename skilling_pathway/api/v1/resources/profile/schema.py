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
            if data.get('current_skills'):
                current_skills = data.get('current_skills').split(',')
                new_skill = prof.current_skills
                if new_skill:
                    new_skill.extend(current_skills)
                else:
                    new_skill = current_skills
                new_skill = [*set(new_skill)]
                prof.current_skills=None
            else:
                new_skill = prof.current_skills
            if data.get('other_languages'):
                current_langs = data.get('other_languages').split(',')
                new_langs = prof.other_languages
                if new_langs:
                    new_langs.extend(current_langs)
                else:
                    new_langs = current_langs
                new_langs = [*set(new_langs)]
                prof.other_languages=None
            else:
                new_langs = prof.other_languages
            if data.get("interested_course"):
                current_course= data.get('interested_course').split(',')
                new_course = prof.interested_course
                if new_course:
                    new_course.extend(current_course)
                else:
                    new_course = current_course
                new_course = [*set(new_course)]
                prof.interested_course=None
            else:
                new_course = prof.interested_course
            if data.get("educational_qualifications"):
                current_qualifi = data.get('educational_qualifications').split(',')
                new_qualifi = prof.educational_qualifications
                if new_qualifi:
                    new_qualifi.extend(current_qualifi)
                else:
                    new_qualifi = current_qualifi
                new_qualifi = [*set(new_qualifi)]
                prof.educational_qualifications=None
            else:
                new_qualifi = prof.educational_qualifications
            if data.get("experience"):
                current_experience = data.get('experience').split(',')
                new_experience = prof.experience
                if new_experience:
                    new_experience.extend(current_experience)
                else:
                    new_experience = current_experience
                new_experience = [*set(new_experience)]
                prof.experience=None
            else:
                new_experience = prof.experience
            session.commit()

            prof.current_skills=new_skill
            prof.other_languages=new_langs
            prof.interested_course=new_course
            prof.educational_qualifications=new_qualifi
            prof.address=data.get('address')
            prof.email=data.get('email')
            prof.mobile=data.get('mobile')
            prof.gender=data.get('gender')
            prof.resume_added = True
            prof.experience = new_experience
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
    
def profile_update(data,id):
    try:
        prof = session.query(ParticipantProfile).filter(ParticipantProfile.id==id).first()
        if prof:
            current_skills = data.get('current_skills')
            if current_skills:
                current_skills = data.get('current_skills').split(',')
            current_langs = data.get('other_languages')
            if current_langs:
                current_langs = data.get('other_languages').split(',')
            current_course= data.get('interested_course')
            if current_course:
                current_course= data.get('interested_course').split(',')
            current_qualifi = data.get('educational_qualifications')
            if current_qualifi:
                current_qualifi = data.get('educational_qualifications').split(',')
            current_experience = data.get('experience')
            if current_experience:
                current_experience = data.get('experience').split(',')
            preferred_course_language = data.get('preferred_course_language')
            if preferred_course_language:
                preferred_course_language = data.get('preferred_course_language').split(',')
            preferred_employment_type = data.get('preferred_employment_type')
            if preferred_employment_type:
                preferred_employment_type = data.get('preferred_employment_type').split(',')
            preferred_job_location_city = data.get('preferred_job_location_city')
            if preferred_job_location_city:
                preferred_job_location_city = data.get('preferred_job_location_city').split(',')
            preferred_job_location_state = data.get('preferred_job_location_state')
            if preferred_job_location_state:
                preferred_job_location_state = data.get('preferred_job_location_state').split(',')
            if data.get('preferred_job_role'):
                preferred_job_role = data.get('preferred_job_role').split(',')
            preferred_work_place_type = data.get('preferred_work_place_type')
            if preferred_work_place_type:
                preferred_work_place_type = data.get('preferred_work_place_type').split(',')

            prof.current_skills=current_skills
            prof.other_languages=current_langs
            prof.interested_course=current_course
            prof.educational_qualifications=current_qualifi
            prof.address=data.get('address')
            # prof.email=data.get('email')
            # prof.mobile=data.get('mobile')
            prof.gender=data.get('gender')
            prof.summary=data.get('summary')
            prof.resume_added = True
            prof.experience = current_experience
            prof.highest_education = data.get('highest_education')
            prof.preferred_course_language = preferred_course_language
            prof.preferred_employment_type = preferred_employment_type
            prof.preferred_job_location_city = preferred_job_location_city
            prof.preferred_job_location_state = preferred_job_location_state
            prof.preferred_job_role = preferred_job_role
            prof.preferred_work_place_type = preferred_work_place_type
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
