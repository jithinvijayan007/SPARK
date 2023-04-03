import json
from datetime import datetime
from flask import Response
from sqlalchemy import or_, and_
from sqlalchemy.orm import aliased

from skilling_pathway.api.v1.decorators import authenticate
from skilling_pathway.api.v1.json_encoder import AlchemyEncoder
from skilling_pathway.api.v1.resources.Resource import API_Resource, NameSpace
from flask import request, current_app
import requests
from skilling_pathway.db_session import session

from .parser_helper import *
from .schema import *

from skilling_pathway.models.profile import *

api = NameSpace("profile")


# api to update profile from pre assessment form parsed data


class ProfileCreateUpdateAPI(API_Resource):
    @authenticate
    @api.expect(profile_create_update_parser)
    def post(self):
        try:
            data = profile_create_update_parser.parse_args()
            participant_id = data.get("participant_id")
            form_response = data.get("form_response")

            # get form response
            form_response = json.loads(form_response)

            # parse form response
            profile_data = {}
            required_fields = [
                "Highest Educational Qualification? (for e.g. 10th Pass)",
                "English Speaking Level?",
                "Other Languages?",
                "Current Skills",
                "Which Courses are you looking for?",
                "Preferred Course Language",
                "Are you currently employed?",
                "Current Employment Details",
                "Start Date",
                "End Date",
                "Preferred Job Location (State)",
                "Preferred Job Location (City)",
                "Preferred Employment Type?",
                "Preferred Workplace?",
                "Preferred Job Role?",
            ]
            for response in form_response:
                if response.get("question_name") in required_fields and response.get("answer"):
                    if response.get("question_name") == 'Highest Educational Qualification? (for e.g. 10th Pass)':
                        profile_data['highest_education'] = response.get("answer")
                    elif response.get("question_name") == 'English Speaking Level?':
                        profile_data['english_speaking_level'] = response.get("answer")
                    elif response.get("question_name") == 'Other Languages?':
                        profile_data['other_languages'] = response.get("answer").split(",")
                    elif response.get("question_name") == 'Current Skills':
                        profile_data['current_skills'] = response.get("answer").split(",")
                    elif response.get("question_name") == 'Which Courses are you looking for?':
                        profile_data['interested_course'] = response.get("answer").split(",")
                    elif response.get("question_name") == 'Preferred Course Language':
                        profile_data['preferred_course_language'] = response.get("answer").split(",")
                    elif response.get("question_name") == 'Are you currently employed?':
                        profile_data['current_employment_status'] = response.get("answer") == 'Yes'
                    elif response.get("question_name") == 'Current Employment Details':
                        profile_data['current_employment_details'] = response.get("answer")
                    elif response.get("question_name") == 'Start Date':
                        profile_data['employment_start_date'] = response.get("answer")
                    elif response.get("question_name") == 'End Date':
                        profile_data['employment_end_date'] = response.get("answer")
                    elif response.get("question_name") == 'Preferred Job Location (State)':
                        profile_data['preferred_job_location_state'] = response.get("answer").split(",")
                    elif response.get("question_name") == 'Preferred Job Location (City)':
                        profile_data['preferred_job_location_city'] = response.get("answer").split(",")
                    elif response.get("question_name") == 'Preferred Employment Type?':
                        profile_data['preferred_employment_type'] = response.get("answer")
                    elif response.get("question_name") == 'Preferred Workplace?':
                        profile_data['preferred_work_place_type'] = response.get("answer")
                    elif response.get("question_name") == 'Preferred Job Role?':
                        profile_data['preferred_job_role'] = response.get("answer").split(",")
            print(profile_data)
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "status": False,
                "message": "Something went wrong",
                "error": str(e),
            }, 500
