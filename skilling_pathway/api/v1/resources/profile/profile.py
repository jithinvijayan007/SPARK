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
from ....extensions import client

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
                if response.get("question_name") in required_fields and response.get(
                    "answer"
                ):
                    if (
                        response.get("question_name")
                        == "Highest Educational Qualification? (for e.g. 10th Pass)"
                    ):
                        profile_data["highest_education"] = response.get("answer")
                    elif response.get("question_name") == "English Speaking Level?":
                        profile_data["english_speaking_level"] = [
                            x.strip()
                            for x in response.get("answer").split(",")
                            if x.strip()
                        ]
                    elif response.get("question_name") == "Other Languages?":
                        profile_data["other_languages"] = [
                            x.strip()
                            for x in response.get("answer").split(",")
                            if x.strip()
                        ]
                    elif response.get("question_name") == "Current Skills":
                        profile_data["current_skills"] = [
                            x.strip()
                            for x in response.get("answer").split(",")
                            if x.strip()
                        ]
                    elif (
                        response.get("question_name")
                        == "Which Courses are you looking for?"
                    ):
                        profile_data["interested_course"] = [
                            x.strip()
                            for x in response.get("answer").split(",")
                            if x.strip()
                        ]
                    elif response.get("question_name") == "Preferred Course Language":
                        profile_data["preferred_course_language"] = [
                            x.strip()
                            for x in response.get("answer").split(",")
                            if x.strip()
                        ]
                    elif response.get("question_name") == "Are you currently employed?":
                        profile_data["current_employment_status"] = (
                            response.get("answer") == "Yes"
                        )
                    elif response.get("question_name") == "Current Employment Details":
                        profile_data["current_employment_details"] = response.get(
                            "answer"
                        )
                    elif response.get("question_name") == "Start Date":
                        profile_data["employment_start_date"] = response.get("answer")
                    elif response.get("question_name") == "End Date":
                        profile_data["employment_end_date"] = response.get("answer")
                    elif (
                        response.get("question_name")
                        == "Preferred Job Location (State)"
                    ):
                        profile_data["preferred_job_location_state"] = [
                            x.strip()
                            for x in response.get("answer").split(",")
                            if x.strip()
                        ]
                    elif (
                        response.get("question_name") == "Preferred Job Location (City)"
                    ):
                        profile_data["preferred_job_location_city"] = [
                            x.strip()
                            for x in response.get("answer").split(",")
                            if x.strip()
                        ]
                    elif response.get("question_name") == "Preferred Employment Type?":
                        profile_data["preferred_employment_type"] = [
                            x.strip()
                            for x in response.get("answer").split(",")
                            if x.strip()
                        ]
                    elif response.get("question_name") == "Preferred Workplace?":
                        profile_data["preferred_work_place_type"] = [
                            x.strip()
                            for x in response.get("answer").split(",")
                            if x.strip()
                        ]
                    elif response.get("question_name") == "Preferred Job Role?":
                        profile_data["preferred_job_role"] = [
                            x.strip()
                            for x in response.get("answer").split(",")
                            if x.strip()
                        ]
            print(profile_data)
            if not (
                profile := session.query(ParticipantProfile)
                .filter(ParticipantProfile.participant_id == participant_id)
                .first()
            ):
                # create profile
                profile = ParticipantProfile(**profile_data)
                session.add(profile)
                session.commit()
                profile.participant_id = participant_id
                session.commit()
                return {"status": True, "message": "Profile created successfully"}, 200
            else:
                # update profile with appending the data to array fields only if they don't exist
                # define a list of fields that can be appended to
                appendable_fields = [
                    "english_speaking_level",
                    "other_languages",
                    "current_skills",
                    "interested_course",
                    "preferred_course_language",
                    "preferred_job_location_state",
                    "preferred_job_location_city",
                    "preferred_employment_type",
                    "preferred_work_place_type",
                    "preferred_job_role",
                ]

                # loop through each field in profile_data and update profile
                for field, value in profile_data.items():
                    # handle appendable fields separately
                    if field in appendable_fields:
                        # only append to the field if it doesn't exist yet
                        if not getattr(profile, field):
                            setattr(profile, field, value)
                        else:
                            existing_values = getattr(profile, field)
                            # convert existing values to lowercase
                            existing_values_lower = [
                                val.lower() for val in existing_values
                            ]
                            # convert new values to lowercase
                            new_values_lower = [val.lower() for val in value]
                            # combine and remove duplicates
                            combined_values_lower = list(
                                set(existing_values_lower + new_values_lower)
                            )
                            # convert back to original case
                            combined_values = [
                                val.title() for val in combined_values_lower
                            ]
                            setattr(profile, field, combined_values)
                    else:
                        setattr(profile, field, value)

                # commit the changes
                session.commit()

                return {"status": True, "message": "Profile updated successfully"}, 200

        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "status": False,
                "message": "Something went wrong",
                "error": str(e),
            }, 500


# profile get api
class ProfileGetAPI(API_Resource):
    @authenticate
    @api.expect(participant_profile_get_parser)
    def get(self, participant_id):
        try:
            args = participant_profile_get_parser.parse_args()
            if not (profile := session.query(ParticipantProfile).filter(
                ParticipantProfile.participant_id == participant_id
            ).first()):
                return {"status": False, "message": "Profile not found"}, 404
            else:
                profile_data = json.loads(json.dumps(profile, cls=AlchemyEncoder))
                return {"status": True, "data": profile_data}, 200
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "status": False,
                "message": "Something went wrong",
                "error": str(e),
            }, 500


# new profile post api with mongodb database
class ProfileAPI(API_Resource):

    def get(self):
        collection = client.skilling_pathway.get_collection("participant_profile")
        profile = collection.find()
        return {"status": True, "data": list(profile)}, 200

    def post(self):
        collection = client.skilling_pathway.get_collection("participant_profile")
        new_work_experiences = [
            {
                "title": "Software Developer",
                "company": "ABC Inc",
                "start_date": "2020-01-01",
                "end_date": "2021-01-01"
            },
            {
                "title": "Data Analyst",
                "company": "XYZ Corp",
                "start_date": "2019-01-01",
                "end_date": "2020-01-01"
            }
        ]
        profile = collection.insert_one({
            "participant_id": "5f9f1b5b9b9b9b9b9b9b9b9b",
            "first_name": "John",
            "last_name": "Doe"
        })
        collection.update_one(
            {"_id": profile.inserted_id},
            {"$push": {"work_experiences": {"$each": new_work_experiences}}}
        )

        return {"status": True, "data": str(profile.inserted_id)}, 200
    

class ProfileResumeUpdateApi(API_Resource):    
    @api.expect(profile_update_resume_parser)
    @authenticate
    def put(self, id):
        
        data = profile_update_resume_parser.parse_args()
        resp = profile_resume_update(data, id)
        return resp
    

class ProfileStatusUpdateAPI(API_Resource):    
    @api.expect(profile_update_parser)
    @authenticate
    def put(self, id):
        
        profile = session.query(ParticipantProfile).filter(ParticipantProfile.id==id).first()
        if profile:
            profile.resume_added = True
            session.commit()
            return {
                    "message": "success",
                    "status": True,
                    "data": {}
                }, 200
        return {
                    "message": "profile not found",
                    "status": False,
                    "data": {}
                }, 400
