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
