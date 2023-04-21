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
from skilling_pathway.models.course import *


def course_grant_create(data,user):
    try:
        course_grant=CourseGrantMaster(
                    participant_id=data.get("participant_id"),
                    course_id=data.get("course_id"),
                    funder_id=data.get("funder_id"),
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