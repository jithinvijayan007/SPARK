from http.client import HTTPException
import json
import math
import copy
from io import BytesIO
from flask import send_file
import os
from sqlite3 import ProgrammingError
from urllib.error import HTTPError
import pandas as pd
from sqlalchemy import func
from skilling_pathway.api.v2.decorators import authenticate
import boto3, botocore
from skilling_pathway.api.v1.models.program.programs import Events
from skilling_pathway.api.v2.json_encoder import AlchemyEncoder, ProgramEncoder
from skilling_pathway.api.v2.resources.Resource import API_Resource, NameSpace
from flask import request, current_app
import numpy as np
import requests
from skilling_pathway.api.config import config
from skilling_pathway.db_session import session
from skilling_pathway.api.v2.models.form import FormMaster, UserFormResponse
from skilling_pathway.api.v2.models.project import (FunderMaster,
                                            PartnerMaster,
                                            AreaFocus,
                                            PrimaryParticipants,
                                            StateCity,
                                            ProgramDetailMaster,
                                            DeliverableDetails,
                                            Instrument,
                                            ActivityDetails,
                                            ProjectEntityMapper,
                                            TaskDetails)
from skilling_pathway.api.v2.decorators import handle_response
from skilling_pathway.api.v2.models.project.project import CommentThread, EntityDetails, Intervention, ProjectDetailMaster, ProjectDetailMaster, Occupation, ParticipantMaster, SPOCMaster
from .parser_helper import (
    program_list_parser,
    stateparser,
    program_list_parser,
    parse_pagination_params,
    parse_pagination_param,
    upload_program_csv_parser,
    intervention_parser,
    intervention_get_parser,
    interventionparser,
    intervention_post_parser,
    intervention_delete_parser,
    project_create_parser,
    s3_file_upload_parser,
    project_template_parser,
    project_list_parser,
    comment_post_parser,
    comment_list_parser,
    s3_file_delete_parser,
    comment_update_parser,
    project_search_parser,
    project_name_checker_parser,
    participant_create_parser,
    participant_get_parser,
    form_user_response_project_filter,
    form_search_parser,
    project_list_participant,
    form_details_parser,
    parse_project_pagination_params,
    project_search_parser2,
    particpant_bulk_upload_parser,
    state_get_parser,
    loc_get_parser,
    project_enroll_get_parser,
    area_focus_get_parser,
    goodcsr_state_get_parser,
    particpants_get_parser,
    area_focus_id_get_parser,
    goodcsr_state_id_get_parser,
    particpants_id_get_parser,
    unfilled_forms_get_parser,
    occupationparser
    )

from sqlalchemy.orm import load_only
from skilling_pathway.api.v2.resources.utils import get_survay_cto_form
from .schema import (
    comment_data_to_db,
    comment_edit,
    delete_file_to_s3,
    filter_comments,
    insert_activity_data,
    insert_deliverable_data,
    insert_entity_data,
    insert_success_matrix_project_data,
    insert_task_data, 
    intervention_data_in_db, 
    intervention_data_to_db, 
    save_program_to_db_new,
    insert_success_matrix_data,
    insert_success_matrix_excel_data,
    parse_uuid,
    save_project_to_db_,
    update_project,
    update_project_deliverable_data,
    update_project_entity_data,
    update_success_matrix_data,
    update_event_data,
    update_program,
    insert_event_excel_data,
    save_excel_bulk_program_to_db_new,
    allowed_file,
    upload_file_to_s3,
    insert_entity_project_data_bulk_upload,
    insert_event_data_bulk_upload,
    save_project_to_db_new_bulk_upload,
    upload_media_file_to_s3,
    get_entity_ids,
    particpant_on_boarding,
    get_project_list,
    particpant_details,
    project_details_data,
    project_list_data,
    particpant_bulk_upload,
    validate_field_bulk,
    good_csr_integration_api,
    good_csr_project_builder_api,
    funder_details,
    ip_details,
    good_csr_project_update_api,
    project_exist_or_not,
    deliverable_payload_manipulation
                     
                     )
from sqlalchemy import or_,and_
from uuid import UUID
from werkzeug.exceptions import NotFound
from flask import g
api = NameSpace('Program')

def validate_field(data,l):
    validation_dict = []
    if not data.get('project_name'):
        validation_dict.append(f"Project Name Required")
    if not data.get('program_name'):
        validation_dict.append(f"Program Name Required")
    if not data.get('key_intervention'):
        validation_dict.append(f"key_intervention Required")
    if not data.get('sub_intervention'):
        validation_dict.append(f"sub_intervention Required")
    
    if not data.get('project_description'):
        validation_dict.append(f"project_description Required")
    if not data.get('project_tagline'):
        validation_dict.append(f"project_tagline Required")
    if not data.get('project_keywords'):
        validation_dict.append(f"project_keywords Required")
    if not data.get('primary_area_of_focus'):
        validation_dict.append(f"primary_area_of_focus Required")
    if not data.get('primary_participants'):
        validation_dict.append(f"primary_participants Required")
    # if not data.get('project_timeline'):
    #     validation_dict.append(f"project_timeline Required")
    if not data.get('project_start_date'):
        validation_dict.append(f"project start date Required")
    if not data.get('project_end_date'):
        validation_dict.append(f"project end date Required")
    if not data.get('outcomes'):
        validation_dict.append(f"outcomes Required")
    if not data.get('impact_generated'):
        validation_dict.append(f"impact_generated Required")
    if not data.get('output'):
        validation_dict.append(f"output Required")
    if not data.get('instruments'):
        validation_dict.append(f"instruments Required")
    if not data.get('city'):
        validation_dict.append(f"city Required")
    if not data.get('district'):
        validation_dict.append(f"district Required")
    if not data.get('state'):
        validation_dict.append(f"state Required")
    if validation_dict:
        raise ValueError(', '.join(validation_dict))

def validate_field_project(data,entity_details):
    validation_dict = []
    if not data.get('project_name'):
        validation_dict.append(f"Project Name Required")
    re=json.loads(entity_details)
    res = [ sub['entity_name'] for sub in re ]

    if res==['']:
        validation_dict.append(f"Entity Name Required")
    if validation_dict:
        raise ValueError(', '.join(validation_dict))



def parse_program_id(program_id):
    try:
        program_id = str(UUID(program_id))
    except Exception:
        session.rollback()
        session.commit()
        raise ValueError("program id is invalid")
    else:
        return program_id


class FundmasterListAPI(API_Resource):
    def get(self):
        try:
            fields = ['id', 'company_name']
            qs = session.query(FunderMaster).options(
                load_only(*fields)).order_by(FunderMaster.id).all()
            serialized_entries = [
                {'id': str(record.id), 'company_name': record.company_name} for record in qs]
            return {
                "message": "success",
                'data': serialized_entries,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400


class PartnerMasterListAPI(API_Resource):
    def get(self):
        try:
            fields = ['id', 'name']
            qs = session.query(PartnerMaster).options(
                load_only(*fields)).order_by(PartnerMaster.id).all()
            serialized_entries = [
                {'id': str(record.id), 'name': record.name} for record in qs]
            return {
                "message": "success",
                'data': serialized_entries,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400


class AreaFocusListAPI(API_Resource):
    def get(self):
        try:
            fields = ['id', 'area_of_focus']
            qs = session.query(AreaFocus).options(
                load_only(*fields)).order_by(AreaFocus.id).all()
            serialized_entries = [
                {'id': str(record.id), 'area_of_focus': record.area_of_focus} for record in qs]
            return {
                "message": "success",
                'data': serialized_entries,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": f"{str(e)} Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"

            }, 400


class PrimaryParticipantsListAPI(API_Resource):
    def get(self):
        try:
            fields = ['id', 'participant_name']
            participents = session.query(PrimaryParticipants).options(
                load_only(*fields)).order_by(PrimaryParticipants.id).all()
            serialized_entries = [{'id': str(
                record.id), 'participant_name': record.participant_name} for record in participents]
            return {
                "message": "success",
                'data': serialized_entries,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400


class StateCityAPI(API_Resource):
    @api.expect(stateparser)
    def get(self):
        try:
            data = stateparser.parse_args()
            params = data.get('params')
            state_id = data.get("state_ids")
            fields = ['id', 'name']
            if not state_id and not params:
                qs = session.query(StateCity).options(load_only(
                    *fields)).filter(StateCity.parent_id == 0).order_by(StateCity.id).all()
                serialized_entries = [
                    {'id': str(record.id), 'name': record.name} for record in qs]
            else:
                if params=='city':
                    qs = session.query(StateCity).options(load_only(
                        *fields)).filter(StateCity.type==params).order_by(StateCity.id).all()
                    serialized_entries = [
                        {'id': str(record.id), 'name': record.name} for record in qs]

                else:
                    qs = session.query(StateCity).options(load_only(
                        *fields)).filter(StateCity.parent_id.in_(state_id)).order_by(StateCity.id).all()
                    serialized_entries = [
                        {'id': str(record.id), 'name': record.name} for record in qs]

            return {
                "message": "success",
                'data': serialized_entries,
                "status": True,
                "type": "success"
            }, 200

        except ZeroDivisionError as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400


class EventListAPI(API_Resource):
    def get(self):
        try:
            fields = ['id', 'name']
            events = session.query(Events).options(
                load_only(*fields)).order_by(Events.id).all()
            serialized_entries = [
                {'id': str(record.id), 'name': record.name} for record in events]
            return {
                "message": "success",
                'data': serialized_entries,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400

class InstrumentListAPI(API_Resource):
    def get(self):
        try:
            fields = ['id', 'name']
            instruments = session.query(Instrument).options(
                load_only(*fields)).order_by(Instrument.id).all()
            serialized_entries = [
                {'id': str(record.id), 'name': record.name} for record in instruments]
            return {
                "message": "success",
                'data': serialized_entries,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400


class ProgramDeleteEdit(API_Resource):
    def get(self, id):
        try:
            id = parse_uuid(id, 'program')
            program = session.query(ProgramDetailMaster).filter(
                ProgramDetailMaster.id == id).first()
            serialized_entries = json.loads(
                json.dumps(program, cls=ProgramEncoder)
            )
            return {'data': serialized_entries}
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400

    def put(self, id):
        '''
        sample payload

        '''

        try:
            id = parse_uuid(id, 'program')
            program = session.query(ProgramDetailMaster).filter(
                ProgramDetailMaster.id == id).first()
            if not program:
                return {
                    "message": "program does not exist",
                    "status": False,
                    "type": "custom_error",
                }, 400
            data = request.form
            file_data = request.files
            success_matrix_ids = update_success_matrix_data(
                data.get('success_matrix'))
            event_ids = update_event_data(data.get('events'))
            update_program(data, file_data, program,
                           success_matrix_ids, event_ids)
            return {
                "type": "success_message",
                "status": True,
                'data': {}
            }, 201
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400

    @handle_response
    def delete(self, id):
        try:
            id = parse_uuid(id, 'program')
            program = session.query(ProgramDetailMaster).filter(
                ProgramDetailMaster.id == id).first()
            program.is_active = False
            # session.add(program)
            session.commit()
            return {
                "type": "success_message",
                "status": True
            }, 202
        except Exception as e:
            session.rollback()
            session.commit()
            print("Exception", e)
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error",
            }, 400



# class ListDeleverableByProject(API_Resource):
#     def get(self, id):
#         try:
#             import pdb;pdb.set_trace()
#             id = parse_uuid(id, 'project')
#             project = session.query(ProjectDetailMaster).filter(
#                 ProjectDetailMaster.id == id).first()
#             if not project:
#                 return {
#                     "message": "project does not exist",
#                     "status": False,
#                     "type": "custom_error",
#                 }, 400
#             deliverables = []  
             
#             deliverable_ids = project.deliverable
#             print(deliverable_ids)
#             deleverables = session.query(DeliverableDetails).filter(DeliverableDetails.id.in_(deliverable_ids)).all()
#             # options(
#                 # load_only(*fields)).
#             activities = [] 
#             for id in deleverables:
#                 activity = session.query(ActivityDetails).filter(ActivityDetails.id.in_(id.activities)).all()
                
#                 activities.append({'id':str(id.id),'name':id.name})

#                 tasks = []
#                 for comnt in activity:
#                     activity = session.query(TaskDetails).filter(TaskDetails.id.in_(comnt.tasks)).all()
#                     # created_at = str( comnt.created_at)
#                     # updated_at = str( comnt.updated_at)
#                     tasks.append({'id':str(comnt.id),'name':comnt.name})
#             deliverables.append({'id':str(comnt.id),'name':comnt.name})
#                     # for item in main_comments:
#                     #     item['reply_comments'] = reply_comments
                

#                 # main_comments["reply_comments"].append(reply_comments)
#                 # main_comments.append({'reply_comments':reply_comments})         

#             serialized_entries = {'comments':deliverables}
#             return serialized_entries
#         except Exception as e:
#             session.rollback()
#             session.commit()
#             return {
#                 "message": str(e),
#                 "status": False,
#                 "type": "custom_error"
#             }, 400


def get_or_none(model_name,id):
    try:
        qs = session.query(model_name).filter(model_name.id==id).first()
        return qs
    except Exception as e:
        session.rollback()
        return None
class ListDeleverable(API_Resource):
    def get(self):
        try:             
            deleverables = session.query(DeliverableDetails).all()
            deliverable_activity_tasks = []
            for deliverable in deleverables:
                delivarable_name = deliverable.name
                activities_id = deliverable.activities
                activity_str = ''
                for activity_id in activities_id:
                    activity_obj = get_or_none(ActivityDetails,activity_id)
                
                
                
            serialized_entries = [
            {'id': str(record.id), 'name': record.name} for record in deleverables]
            return {
                "message": "success",
                'data':serialized_entries,
                "status": True,
                "type": "success"
            }, 200
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400

class ListEventByProgram(API_Resource):
    def get(self, id):
        try:
            fields = ['id', 'name']
            id = parse_uuid(id, 'project')
            project = session.query(ProgramDetailMaster).filter(
                ProgramDetailMaster.id == id).first()
            if not project:
                return {
                    "message": "program does not exist",
                    "status": False,
                    "type": "custom_error",
                }, 400
            event_ids = project.events
            print(event_ids)
            events = session.query(Events).options(
                load_only(*fields)).filter(Events.id.in_(event_ids)).all()
            serialized_entries = [{'id': str(data.id),
                                   'name': data.name
                                   } for data in events]
            return {'data': serialized_entries}
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400



class ListFromsByProject(API_Resource):
    @api.expect(form_search_parser)
    def get(self, program_id):
        try:
            # fields = ['id', 'form_name','form_description']
            program_id = parse_uuid(program_id, 'program')
            # forms = session.query(FormMaster).options(load_only(*fields)).\
            #     filter_by(is_active=True).\
            #     filter(FormMaster.project == program_id).all()
            # serialized_entries = [{'id': str(data.id),
            #                        'name': data.form_name,
            #                        'form_description':data.form_description
            #                        } for data in forms]
            # return {'data': serialized_entries}

            
            data = form_search_parser.parse_args()
            if any(data.values()):
                conditions = []
                if data.get('form_name'):
                    form_name = data.get('form_name').lower()
                    conditions.append(func.lower(FormMaster.form_name).contains(
                        form_name))
                if data.get('present_status'):
                    present_status = data.get('present_status')
                    conditions.append(FormMaster.present_status==present_status.lower())
                if data.get('creation_date'):
                        conditions.append(FormMaster.form_creation_date==data.get('creation_date'))
                if data.get('form_type'):
                    if data.get('form_type') != 'all':
                        conditions.append(FormMaster.type==data.get('form_type'))
                if data.get('id'):
                    form_uuid = parse_uuid(data.get('id'),'form')
                    conditions.append(FormMaster.id==form_uuid)            
                programs = session.query(FormMaster).\
                        filter_by(is_active=True).filter(FormMaster.project == program_id).\
                        order_by(FormMaster.present_status.desc(), FormMaster.created_at.asc()).\
                            filter(or_(*conditions)).all()
            
            else:
                programs = session.query(FormMaster).filter_by(is_active=True).filter(FormMaster.project == program_id).\
                        order_by(FormMaster.present_status.desc(), FormMaster.created_at.asc()).all()
            
            serialized_entries = json.loads(
                json.dumps(programs, cls=AlchemyEncoder)
            )
            serialized_entries = serialized_entries[0] if data.get('id') and serialized_entries else serialized_entries
            
            return {
                "message": "success",
                'data':serialized_entries,
                "status": True,
                "type": "success"
            }, 200



        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400

class ListProgramDropDown(API_Resource):
    def get(self):
        try:
            fields = ['id', 'program_name']
            programs = session.query(ProgramDetailMaster).options(
                load_only(*fields)).order_by(ProgramDetailMaster.id).all()
            serialized_entries = [
                {'id': str(record.id), 'name': record.program_name} for record in programs]
            return {
                "message": "success",
                'data': serialized_entries,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400


def missing_columns(events):
    logs = [record[0]
            for event_obj in events for record in event_obj.items() if not record[1]]
    return logs


class BulkUploadProgramAPI(API_Resource):
    @authenticate
    @api.expect(upload_program_csv_parser)
    @handle_response
    def post(self):
        try:
            date_validation_error = []
            file = upload_program_csv_parser.parse_args()
            program_df = pd.read_excel(file.file, sheet_name='Program')
            events_df = pd.read_excel(file.file, sheet_name='Event')
            success_matrix_df = pd.read_excel(
                file.file, sheet_name='SuccessMatrix')
            program_names = {'ProgramID': 'id',
                             'ProgramName': 'program_name',
                             'ProgramDescription': 'program_description',
                             'ProgramTagline': 'program_tagline',
                             'AreaFocus': 'primary_area_of_focus',
                             'PrimaryParticipents': 'primary_participants',
                             'No.Participents': 'no_of_participants',
                             'PrimaryTimeLine(Months)': 'program_timeline',
                             'ProgramStartDate': 'program_start_date',
                             'ProgramEndDate': 'program_end_date',
                             'Instruments': 'instruments',
                             'ProgramBudget(INR)': 'budget',
                             'ProgramKeywords': 'keywords',
                             'LocationCategory': 'location_category',
                             'State': 'state',
                             'City': 'city',
                             'ProgramOutput': 'output',
                             'Funder': 'funder',
                             'ImplementationPartner': 'implementation_partner',
                             'ProgramProfileImage': 'profile_image',
                             'ProgramCoverImage': 'cover_image',
                             'ImpactGeneratedFromProgram': 'impact_generated',
                             'MOU': 'mou',
                             'ProgramOutcomes': 'outcomes',

                             }
            program_df.rename(columns=program_names, inplace=True)
            program_invalid_date = program_df.loc[program_df['program_start_date']
                                                  > program_df['program_end_date'], 'id']
            program_invalid_date_fields = [{'ProgramID': program_id,
                                            "missing_values": [],
                                            'message':'ProgramStartDate should be less than ProgramEndDate'
                                            } for program_id in program_invalid_date]

            program_df = program_df.loc[program_df['program_start_date']
                                        < program_df['program_end_date'], :]
            program_df['program_start_date'] = program_df['program_start_date'].dt.date.astype(
                str)
            program_df['program_end_date'] = program_df['program_end_date'].dt.date.astype(
                str)

            success_matrix_df_invalid_date = success_matrix_df.loc[
                success_matrix_df['StartDate'] > success_matrix_df['TargetDate'], 'ProgramID']
            events_df_invalid_date = events_df.loc[events_df['StartDate']
                                                   > events_df['TargetDate'], 'ProgramID']
            success_matrix_invalid_pgm_ids = [{
                "ProgramID": i,
                'missing_values': [],
                'message':'success_matrix StartDate should be lessthan TargetDate'}
                for i in success_matrix_df_invalid_date]

            events_invalid_pgm_ids = [{
                "ProgramID": i,
                'missing_values': [],
                'message':'Events StartDate should be less than TargetDate'}
                for i in events_df_invalid_date]
            events_df = events_df.loc[events_df['StartDate']
                                      < events_df['TargetDate'], :]
            success_matrix_df = success_matrix_df.loc[success_matrix_df['StartDate']
                                                      < success_matrix_df['TargetDate'], :]
            program_invalid_date_fields = [*success_matrix_invalid_pgm_ids,
                                           *events_invalid_pgm_ids]
            success_matrix_df['StartDate'] = success_matrix_df['StartDate'].dt.date.astype(
                str)
            success_matrix_df['TargetDate'] = success_matrix_df['TargetDate'].dt.date.astype(
                str)

            events_df['StartDate'] = events_df['StartDate'].dt.date.astype(str)
            events_df['TargetDate'] = events_df['TargetDate'].dt.date.astype(
                str)
            program_data = json.loads(program_df.to_json(orient='records'))
            missing_values = []
            db_logs = []
            for program_obj in program_data:
                events = json.loads(
                    events_df.loc[events_df['ProgramID'] == program_obj['id'], :].to_json(orient='records'))
                success_matrix = json.loads(
                    success_matrix_df.loc[success_matrix_df['ProgramID'] == program_obj['id'], :].to_json(orient='records'))

                program_error_logs = [(r[0])
                                      for r in program_obj.items() if not r[1]]
                events_error_logs = missing_columns(events)
                success_matrix_error_logs = missing_columns(success_matrix)
                if not program_error_logs and not events_error_logs and not success_matrix_error_logs:
                    if not events or not success_matrix:
                        missing_fields = []
                        if not events:
                            missing_fields.append('event')
                        if not success_matrix:
                            missing_fields.append('success_matrix')

                        db_logs.append({'ProgramID': int(program_obj['id']),
                                        'missing_values': missing_fields,
                                        'message': ''})
                    else:
                        s = program_obj['id']
                        print(f'{s}')
                        success_matrix_ids = insert_success_matrix_excel_data(
                            success_matrix)
                        program_events_ids = insert_event_excel_data(events)
                        save_excel_bulk_program_to_db_new(
                            program_obj, success_matrix_ids, 
                            program_events_ids)
                        # Write Logic DB Insertion
                        # program_obj
                        # events
                        # success_matrix

                else:
                    missing_values.append({'ProgramID': int(program_obj['id']),
                                           'missing_values': [*program_error_logs, *success_matrix_error_logs, *events_error_logs],
                                           'message': ''}
                                          )

            # import pdb;pdb.set_trace()
            # success_matrix_ids = insert_success_matrix_excel_data(data.get('success_matrix'))
            # program_events_ids = insert_event_data(events)
            #
            return {
                "type": "success_message",
                "status": True,
                'data': [*missing_values, *db_logs, *program_invalid_date_fields]
            }, 201

        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error",
            }, 400

# class InterventionAPI(API_Resource):
#     @api.expect(intervention_parser)
#     def post(self):
#         try:
#             data = intervention_parser.parse_args()
#             intervention_data_in_db(data)
#             return {
#                     "message": "success",
#                     'data':{},
#                     "status": True,
#                     "type": "success"
#                 }, 200

#         except Exception as e:
#             return {
#                 "message": "Something went wrong, please try after some time",
#                 "status": False,
#                 "type": "custom_error"
#             }, 400
#     @api.expect(intervention_get_parser)
#     def get(self):
#         try:
#             fields = ['id', 'name']
#             data = intervention_get_parser.parse_args()
#             # if intervention_type == 'key_intervention':
#             intervention_data = session.query(Intervention).filter_by(is_active=True).\
#             filter(Intervention.intervention_type == data.get('intervention_type')).all()
#             serialized_entries = [
#             {'id': str(record.id), 'name': record.name} for record in intervention_data]
#             return {
#                 "message": "success",
#                 'data': serialized_entries,
#                 "status": True,
#                 "type": "success"
#             }, 200
            

#         except Exception as e:
#             session.rollback()
#             session.commit()
#             return {
#                 "message": "Something went wrong, please try after some time",
#                 "status": False,
#                 "type": "custom_error"
#             }, 400
            
# class InterventionListAPI(API_Resource):
#     def get(self,intervention_type):
#         try:
#             if intervention_type == 'key_intervention':
#                 intervention_data = session.query(Intervention).filter(
#                 Intervention.intervention_type == intervention_type).all()
#                 serialized_entries = [
#                 {'id': str(record.id), 'name': record.name} for record in intervention_data]
#                 return {
#                     "message": "success",
#                     'data': serialized_entries,
#                     "status": True,
#                     "type": "success"
#                 }, 200

#             elif intervention_type == 'sub_intervention':
#                 intervention_data = session.query(Intervention).filter(
#                 Intervention.intervention_type == intervention_type).all()
#                 serialized_entries = [
#                 {'id': str(record.id), 'name': record.name} for record in intervention_data]
#                 return {
#                     "message": "success",
#                     'data': serialized_entries,
#                     "status": True,
#                     "type": "success"
#                 }, 200
            

#         except Exception as e:
#             session.rollback()
#             session.commit()
#             return {
#                 "message": "Something went wrong, please try after some time",
#                 "status": False,
#                 "type": "custom_error"
#             }, 400

class InterventionAPI(API_Resource):
    @api.expect(interventionparser)
    def get(self):
        try:
            data = interventionparser.parse_args()
            intervention_id = str(data.get("intervention_id")) if data.get("intervention_id") else ''
            fields = ['id', 'name']
            data = []
            if not intervention_id:
                qs = session.query(Intervention).options(load_only(
                    *fields)).filter(Intervention.lookup_id == None).filter(Intervention.is_active == True).order_by(Intervention.id).all()
                key_intervention_entries = [
                    {'id': str(record.id), 'name': record.name} for record in qs]
                return {
                "message": "success",
                'key_data' : key_intervention_entries,
                "status": True,
                "type": "success"
            }, 200

            qs = session.query(Intervention).options(load_only(
                *fields)).filter(Intervention.lookup_id.in_([intervention_id])).filter(Intervention.is_active == True).order_by(Intervention.name).all()
            for record in qs:
                sub_intervention_entries ={'id': str(record.id), 'name': record.name}               

                qd = session.query(Intervention).options(load_only(
                    *fields)).filter(Intervention.lookup_id.in_([str(record.id)])).filter(Intervention.is_active == True).order_by(Intervention.name).all()
                for record in qd: 
                    sub_intervention_entries['project_name'] = record.name
                    
                data.append(sub_intervention_entries)
            return {
                "message": "success",
                'data': data,
                "status": True,
                "type": "success"
            }, 200
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400

    @api.expect(intervention_post_parser)
    def post(self):
        try:
            data = intervention_post_parser.parse_args()
            intervention_data_to_db(data)
            return {
                    "message": "success",
                    'data':{},
                    "status": True,
                    "type": "success"
                }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400
    
    @api.expect(intervention_delete_parser)
    def delete(self):
        try:
            data = intervention_delete_parser.parse_args()
            intervention_id = str(data.get("intervention_id"))
            parse_uuid(intervention_id, 'intervention')
            intervention = session.query(Intervention).filter(
                Intervention.id == intervention_id).first()
            intervention.is_active = False
            lookup_id = []
            qs = session.query(Intervention).filter(Intervention.lookup_id.in_([str(intervention.id)])).filter(Intervention.is_active == True).all()
            for record in qs:
                record.is_active = False 
                lookup_id.append(str(record.id))
            qd = session.query(Intervention).filter(Intervention.lookup_id.in_(lookup_id)).filter(Intervention.is_active == True).all()
            for record in qd:
                record.is_active = False
            session.commit()
            return {
                "type": "success_message",
                "status": True
            }, 202
        except Exception as e:
            session.rollback()
            session.commit()
            print("Exception", e)
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error",
            }, 400

        
class S3ImageUpload(API_Resource):
    @api.expect(s3_file_upload_parser)
    def post(self):
        try:
            data = s3_file_upload_parser.parse_args()
            file = data.get('file')
            url = ''
            if file.filename == '':
                raise FileNotFoundError('No selected file')
            if file and allowed_file(file.filename):
                output = upload_file_to_s3(file)
                if output:
                    bucket= os.getenv("AWS_S3_BUCKET_NAME")
                    BASE_URL = 'uploads/'
                    url = f'https://{bucket}.s3.amazonaws.com/{BASE_URL}{file.filename}'
                    return {'media_url': url},200
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "data": str(e),
                "status": False,
                "type": "custom_error"
            }, 400

        

def get_entity_object(entity_id,entity_df,success_matrix_df):
    entity_id = np.array(entity_id,dtype='int')
    entity_df['EntityId'] = entity_df['EntityId'].astype('int')
    entity = json.loads(entity_df.loc[entity_df.EntityId.isin(entity_id),:].to_json(orient='records'))
    entities = []
    for entity_obj in entity:
        success_matrix_ids = np.array(entity_obj['SuccessMatrix'].split(','),dtype='float')
        success_matrix_data = json.loads(success_matrix_df.loc[success_matrix_df.SuccessMatrixId.isin(success_matrix_ids),:].to_json(orient='records'))
        entity_obj['SuccessMatrix'] = success_matrix_data
        entities.append(entity_obj)
    return entities

def get_events(event_id,event_df):
    event_id = np.array(event_id,dtype='int')
    event_obj = json.loads(event_df.loc[event_df.EventId.isin(event_id),:].to_json(orient='records'))
    return event_obj
    
class BulkProjectUpload(API_Resource):
    @api.expect(project_template_parser)
    def post(self):
        try:
            template = project_template_parser.parse_args()
            template = template.get('template')
            # date validation ---- start 
            project_df = pd.read_excel(template,sheet_name='Project')
            events_df = pd.read_excel(template,sheet_name='Event')
            success_matrix_df = pd.read_excel(template,sheet_name='SuccessMatrix')
            entity_df = pd.read_excel(template,sheet_name='Entity')
            project_df['Event'] = project_df['Event'].astype('str')
            project_df['Entity'] = project_df['Entity'].astype('str')
            
            project_invalid_date = project_df.loc[project_df['ProjectStartDate']
                                                            > project_df['ProjectEndDate'], :].index
            project_invalid_date_fields = [{'ProjectId': project_id,
                                                        "missing_values": [],
                                                        'message':'ProgramStartDate should be less than ProgramEndDate'
                                                        } for project_id in project_invalid_date]

            project_df = project_df.loc[project_df['ProjectStartDate']
                                                    < project_df['ProjectEndDate'], :]

            project_df['ProjectStartDate'] = project_df['ProjectStartDate'].dt.date.astype(
                            str)
            project_df['ProjectEndDate'] = project_df['ProjectEndDate'].dt.date.astype(
                            str)
            # date validation ---- end
            
            # successMatrix date validation ------- start
            success_matrix_df_invalid_date = success_matrix_df.loc[
                success_matrix_df['StartDate'] > success_matrix_df['TargetDate'], 'SuccessMatrixId']
            success_matrix_invalid_pgm_ids = [{
                            "ProgramID": i,
                            'missing_values': [],
                            'message':'success_matrix StartDate should be lessthan TargetDate'}
                            for i in success_matrix_df_invalid_date]

            success_matrix_df = success_matrix_df.loc[success_matrix_df['StartDate']
                                                                < success_matrix_df['TargetDate'], :]
            # successMatrix date validation ------  end
            
            # Event - validation ----- start
            events_df_invalid_date = events_df.loc[
                events_df['StartDate'] > events_df['TargetDate'], 'EventId']
            event_invalid_ids = [{
                            "EventId": i,
                            'missing_values': [],
                            'message':'Event StartDate should be lessthan TargetDate'}
                            for i in events_df_invalid_date]

            events_invalid_df = events_df.loc[events_df['StartDate']
                                                                < events_df['TargetDate'], :]
            # Event Validation ---- End
            project_df['ProjectStartDate'] = project_df['ProjectStartDate'].astype(str)
            project_df['ProjectEndDate'] = project_df['ProjectEndDate'].astype(str)
            
            events_df['StartDate'] = events_df['StartDate'].astype(str)
            events_df['TargetDate'] = events_df['TargetDate'].astype(str)
            
            success_matrix_df['StartDate'] = success_matrix_df['StartDate'].astype(str)
            success_matrix_df['TargetDate'] = success_matrix_df['TargetDate'].astype(str)
            
            project_data = json.loads(project_df.to_json(orient='records'))
            for project_obj in project_data:
                entity_ids = project_obj['Entity'].split(',')
                entity_data = get_entity_object(entity_ids,entity_df,success_matrix_df)
                project_error_log = [k for k,v in project_obj.items() if not v]
                event_id = np.array(project_obj['Event'].split(','))
                events = get_events(event_id,events_df)
                entity_ids = insert_entity_project_data_bulk_upload(entity_data)
                program_events_ids = insert_event_data_bulk_upload(events)
                save_project_to_db_new_bulk_upload(project_obj,entity_ids, program_events_ids)
                
                
            

            

            
            return {
                'message':'records inserted successfully',
                'type':'success_message',
                'errors':[],
                'status':True
                },201
    
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "data": str(e),
                "status": False,
                "type": "custom_error"
            }, 400


class CommentAPI(API_Resource):
    @authenticate
    @api.expect(comment_post_parser)
    def post(self):
        try:
            data = comment_post_parser.parse_args()
            user_id = str(request.user)
            comment_data_to_db(data,user_id)
            return {
                    "message": "success",
                    'data':{},
                    "status": True,
                    "type": "success"
                }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400

    @authenticate
    @api.expect(comment_list_parser)
    def get(self):
        try:
            data = request.args
            access_token = request.headers.get('access-token')
            if data:
                if data.get('project_id'):
                    project_uuid = parse_uuid(data.get('project_id'), 'comment')
                    serialized_entries = filter_comments(project_uuid,access_token)
                    return {
                "message": "success",
                'data': serialized_entries,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "data": str(e),
                "status": False,
                "type": "custom_error"
            }, 400

class CommentS3FileUpload(API_Resource):
    @api.expect(s3_file_upload_parser)
    def post(self):
        try:
            data = s3_file_upload_parser.parse_args()
            file = data.get('file')
            url = ''
            if file.filename == '':
                raise FileNotFoundError('No selected file')
            
            if file:
                output = upload_media_file_to_s3(file)
                if output:
                    bucket= os.getenv("AWS_S3_BUCKET_NAME")
                    BASE_URL = 'uploads/comment_media/'
                    url = f'https://{bucket}.s3.amazonaws.com/{BASE_URL}{file.filename}'
                    return {'media_url': url},200
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "data": str(e),
                "status": False,
                "type": "custom_error"
            }, 400


class S3ImageDelete(API_Resource):
    @api.expect(s3_file_delete_parser)
    def post(self):
        try:
            data = s3_file_delete_parser.parse_args()
            file = data.get('file_name')
            url = ''
            if not file:
                raise FileNotFoundError('No selected file')
            delete_file_to_s3(file)
            return {
                    "message": "success",
                    'data':{},
                    "status": True,
                    "type": "success"
                }, 200
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "data": str(e),
                "status": False,
                "type": "custom_error"
            }, 400

class CommentEditDeleteAPI(API_Resource):
    @api.expect(comment_update_parser)
    def put(self, id):
        try:
            data = comment_update_parser.parse_args()
            id = parse_uuid(id, 'comment')
            comment = session.query(CommentThread).filter(
                CommentThread.id == id).first()
            if not comment:
                return {
                    "message": "comment does not exist",
                    "status": False,
                    "type": "custom_error",
                }, 400
            comment_edit(data, comment)
            return {
                    "message": "success",
                    'data':{},
                    "status": True,
                    "type": "success"
                }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400

        
    @handle_response
    def delete(self, id):
        try:
            id = parse_uuid(id, 'comment')
            comment = session.query(CommentThread).filter(
                CommentThread.id == id).first()
            if not comment:
                return {
                    "message": "comment does not exist",
                    "status": False,
                    "type": "custom_error",
                }, 400
            comment.is_active = False
            session.commit()
            return {
                "type": "success_message",
                "status": True
            }, 202
        except Exception as e:
            session.rollback()
            session.commit()
            print("Exception", e)
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error",
            }, 400

def isSubset(arr1, arr2):
    i = 0
    j = 0
    if len(arr1) < len(arr2):
        return False
 
    arr1.sort()
    arr2.sort()
 
    while i < len(arr2) and j < len(arr1):
        if arr1[j] < arr2[i]:
            j += 1
        elif arr1[j] == arr2[i]:
            j += 1
            i += 1
        elif arr1[j] > arr2[i]:
            return False
    return False if i < len(arr2) else True

def get_distributor_id():
    headers = {
    'Accept': 'application/json',
    'access-token': request.headers['access-token']
    }
    response = requests.request("GET", config.get_distributor_url, headers=headers,)
    return response.json()['data']['distributor_id']

def get_funder_id():
    headers = {
    'Accept': 'application/json',
    'access-token': request.headers['access-token']
    }
    response = requests.request("GET", config.get_funder_url, headers=headers,)
    return response.json()['data']['funder_id']
# def distributor_contact_person(distributor_id):
#     url = f"{config.agent_by_ip_url}/{distributor_id}/contact-person/"
#     payload={}
#     headers = {
#     'accept': 'application/json',
#     'access-token': request.headers['access-token']
#     }
#     response = requests.request("GET", url, headers=headers, data=payload)
#     return response.json()['data']['user_id']
class ProjectMasterAPI1(API_Resource):

    @authenticate
    # @api.expect(project_create_parser)
    @handle_response
    def post(self):
        try:
            data = request.form
            file_data = request.files
            # validate_field(data)
            entity_ids = None
            entity_details = data.get('entity_details')
            validate_field_project(data,entity_details)
            if entity_details:
                entity_ids = insert_entity_data(entity_details)
            deliverable_ids, goodcsr_del_data, goodcsr_activity_data, goodcsr_task_data= insert_deliverable_data(data.get('deliverables'))
            # activity_ids = insert_activity_data(data.get('activities'))
            # task_ids = insert_task_data(data.get('task'))             
            id = save_project_to_db_(data,entity_ids,deliverable_ids,file_data,request.user) 
            project_data = good_csr_integration_api(data, id)
            good_csr_reponse = None
            if project_data:
                goodcsr_del_data = deliverable_payload_manipulation(goodcsr_del_data)
                good_csr_payload = {}
                good_csr_payload['project'] = project_data
                good_csr_payload['deliverable'] = goodcsr_del_data
                good_csr_payload['funder']= funder_details(entity_details)
                i_ps = ip_details(entity_details)
                good_csr_payload['ip'] = i_ps[0]['data']
                good_csr_reponse = good_csr_project_builder_api(good_csr_payload)
            return {
                "type": "success_message",
                "status": True,
                'data': {"id":str(id)},
                "googcsr_response": good_csr_reponse
            }, 201

        except Exception as e:
            session.rollback()
            session.commit()
            print(str(e))
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error",
            }, 400
    
    @authenticate
    @api.expect(project_search_parser)
    def get(self):
        try:
            data = project_search_parser.parse_args()
            start, end, page_size = parse_pagination_params()
            if len(set(data.values()))!=1:
                conditions = []
                if data.get('project_name'):
                    pro_name = data.get('project_name').lower()
                    conditions.append(func.lower(ProjectDetailMaster.project_name).contains(
                        pro_name))
                if data.get('partner'):
                    print(data.get('partner'))
                    ips = data.get('partner').split(',')
                    entity_details = get_entity_ids(ips,'ip')
                    print('entity_details ',entity_details)
                    for partner_id in entity_details:
                        conditions.append(ProjectDetailMaster.entity.any(partner_id))
                if data.get('state'):
                    states = data.get('state').split(',')
                    for state_id in states:
                        conditions.append(
                                ProjectDetailMaster.state.any(state_id))                     
                if data.get('funder'):
                    funders = data.get('funder').split(',')
                    entity_details = get_entity_ids(funders,'funder')
                    for funder_id in entity_details:
                        conditions.append(ProjectDetailMaster.entity.any(funder_id))
                
                if data.get('date'):
                    conditions.append(
                            ProjectDetailMaster.project_start_date == data.get('date'))
                if data.get('id'):
                    project_uuid = parse_uuid(data.get('id'), 'project')
                    conditions.append(ProjectDetailMaster.id == project_uuid)
                if data.get('samhita_id'):
                    samhita_id = data.get('samhita_id').lower()
                    conditions.append(func.lower(ProjectDetailMaster.samhita_id).contains(
                        samhita_id))
                
                projects = session.query(ProjectDetailMaster).\
                        order_by(ProjectDetailMaster.created_at.desc()).\
                        filter(or_(*conditions))
            else:
                projects = session.query(ProjectDetailMaster).\
                    order_by(ProjectDetailMaster.created_at.desc())

            # projects = projects.filter_by(is_active=True).all()
            if request.group.upper() in ['DISTRIBUTOR', 'USER']:
                ip_id = get_distributor_id() # 
                project_data = session.query(EntityDetails,ProjectEntityMapper).filter(
                    EntityDetails.entity_type=='ip'
                    ).join(
                    ProjectEntityMapper,EntityDetails.id==ProjectEntityMapper.entity_id
                    ).all()
                projects_ids = [str(project[1].project_id) for project in project_data if project[0].entity_name==str(ip_id)]
                projects = projects.filter(ProjectDetailMaster.id.in_(projects_ids))
            elif request.group.upper() in ['FUNDER']:
                funder_id = get_funder_id()
                project_data = session.query(EntityDetails,ProjectEntityMapper).filter(
                    EntityDetails.entity_type=='funder'
                    ).join(
                    ProjectEntityMapper,EntityDetails.id==ProjectEntityMapper.entity_id
                    ).all()
                projects_ids = [str(project[1].project_id) for project in project_data if project[0].entity_name==str(funder_id)]
                projects = projects.filter(ProjectDetailMaster.id.in_(projects_ids))
            project_details, total_records = project_details_data(projects,start, end)
            serialized_entries = json.loads(
                json.dumps(project_details, cls=AlchemyEncoder)
            )
            try:
                total_pages = math.ceil(total_records / page_size)
            except Exception as e:
                current_app.error_logger.error("validation error", exc_info=e)
                print(str(e))
                total_pages = 0
            if serialized_entries:
                serialized_entries = serialized_entries[0] if data.get(
                    'id') and project_details else serialized_entries

            return {
                "message": "success",
                'data': serialized_entries,
                "page_size": page_size,
                "total_pages": total_pages,
                "count": total_records,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            # current_app.error_logger.error("validation error", exc_info=e)
            return {
                "message": "Something went wrong, please try after some time",
                "data": str(e),
                "status": False,
                "type": "custom_error"
            }, 400

class ProjectDeleteEditV2API(API_Resource):

    @authenticate
    def put(self, id):
        '''
        sample payload

        '''

        try:
            id = parse_uuid(id, 'project')
            project = session.query(ProjectDetailMaster).filter(
                ProjectDetailMaster.id == id).first()
            if not project:
                return {
                    "message": "project does not exist",
                    "status": False,
                    "type": "custom_error",
                }, 400
            data = request.form
            file_data = request.files
            # validate_field(data)
            entity_details = data.get('entity_details')
            entity_ids = update_project_entity_data(entity_details)
            deliverable_ids, goodcsr_del_data, goodcsr_activity_data, goodcsr_task_data = update_project_deliverable_data(data.get('deliverables'))
            update_project(data, entity_ids, project, deliverable_ids,file_data,entity_details,request.user)
            project_data = good_csr_integration_api(data, id)
            good_csr_reponse = None
            if project_data:
                good_csr_payload = {}
                goodcsr_del_data = deliverable_payload_manipulation(goodcsr_del_data)
                good_csr_payload['project'] = project_data
                good_csr_payload['deliverable'] = goodcsr_del_data
                good_csr_payload['funder']= funder_details(entity_details)
                i_ps = ip_details(entity_details)
                good_csr_payload['ip'] = i_ps[0]['data']
                response = project_exist_or_not(id)
                if response:
                    good_csr_reponse = good_csr_project_update_api(good_csr_payload)
                else:                    
                    good_csr_reponse = good_csr_project_builder_api(good_csr_payload)
            return {
                "type": "success_message",
                "status": True,
                'data': {"id":str(id)},
                "googcsr_response": good_csr_reponse
            }, 201

        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400
    @authenticate
    @handle_response
    def delete(self, id):
        try:
            id = parse_uuid(id, 'project')
            project = session.query(ProjectDetailMaster).filter(
                ProjectDetailMaster.id == id).first()
            if project:
                project.is_active = False
                # forms = session.query(FormMaster).filter(
                #     FormMaster.project == str(project.id)).filter(
                #     FormMaster.is_active ==True).all()
                # if forms:
                #     for form in forms:
                #         form.is_active = False
                session.commit()
                return {
                    "type": "success_message",
                    "status": True
                }, 202
        except Exception as e:
            session.rollback()
            session.commit()
            print("Exception", e)
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error",
            }, 400

class ProjectNameValidator(API_Resource):
    @authenticate
    @api.expect(project_name_checker_parser)
    def post(self):
        try:
            data = project_name_checker_parser.parse_args()
            project_name = data.get('project_name')
            exist = bool(session.query(ProjectDetailMaster).filter_by(project_name=project_name).first())
            if exist:
                return {
                    "message": "project with same name already exist",
                    "status": False,
                    "type": "custom_error",
                }, 400
            return {
                    "message": "success",
                    'data':{},
                    "status": True,
                    "type": "success"
                }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400


class PaticipantOnBoardingAPI(API_Resource):
    @authenticate
    @api.expect(participant_get_parser)
    def get(self):
        try:
            data = participant_get_parser.parse_args()
            if any(data.values()):
                conditions = []
                if data.get('id'):
                    user_id = parse_uuid(data.get('id'),'participant')
                    conditions.append(ParticipantMaster.id==user_id)            
                users = session.query(ParticipantMaster).\
                        filter_by(is_active=True).\
                        order_by(ParticipantMaster.created_at.desc()).\
                            filter(or_(*conditions)).all()
            
            else:
                users = session.query(ParticipantMaster).filter_by(is_active=True).\
                        order_by(ParticipantMaster.created_at.desc()).all()
            
            serialized_entries = [{'id': str(data.id),
                                   'first_name' : data.first_name,
                                   'middle_name' : data.middle_name,
                                    'last_name' : data.last_name,
                                    'use_smartphone' : data.use_smartphone,
                                    'mobile_number' : data.mobile_number,
                                    'any_physical_disability' : data.any_physical_disability,
                                    'details_of_disability' : data.details_of_disability,
                                    'dob' : str(data.dob) if data.dob!=None else None,
                                    'gender' : data.gender,
                                    'marial_status' : data.marial_status,
                                    'native_language' : data.native_language,
                                    'religion' : data.religion,
                                    'caste' : data.caste,
                                    'highest_edu_qualification' : data.highest_edu_qualification,
                                    'enrolled_in_school' : data.enrolled_in_school,
                                    'do_you_have_house' : data.do_you_have_house,
                                    'father_name' : data.father_name,
                                    'mother_name' : data.mother_name,
                                    'guardian_phone_number' : data.guardian_phone_number,
                                    'spouse_name' : data.spouse_name,
                                    'no_of_children' : data.no_of_children,
                                    'no_family_members' : data.no_family_members,
                                    'no_family_member_depandant' : data.no_family_member_depandant,
                                    'no_earning_house_member' : data.no_earning_house_member,
                                    'number_of_siblings' : data.number_of_siblings,
                                    'description_of_degee' : data.description_of_degee,
                                    'address_line1' : data.address_line1,
                                    'address_line2' : data.address_line2,
                                    'village' : data.village,
                                    'city' : data.city,
                                    'state' : data.state,
                                    'district' : data.district,
                                    'pincode' : data.pincode,
                                    'housetype' : data.housetype,
                                    'bank_account_number' : data.bank_account_number,
                                    'bank_name' : data.bank_name,
                                    'ifsc_code' : data.ifsc_code,
                                    'branch' : data.branch,
                                    'any_current_loan' : data.any_current_loan,
                                    'last_loan_apply_date' : str(data.last_loan_apply_date) if data.last_loan_apply_date!=None else None,
                                    'type_of_loan' : data.type_of_loan,
                                    'loan_duration' : data.loan_duration,
                                    'major_expenses' : data.major_expenses,
                                    'total_savings_in_month' : data.total_savings_in_month,
                                    'total_savings_in_year' : data.total_savings_in_year,
                                    'type_of_transport_available_1_2_km' : data.type_of_transport_available_1_2_km,
                                    'amenities_available_at_home' : data.amenities_available_at_home,
                                    'access_electricity' : data.access_electricity,
                                    'access_to_clean_drinkingwater' : data.access_to_clean_drinkingwater,
                                    'source_of_water' : data.source_of_water,
                                    'access_landline_connection' : data.access_landline_connection,
                                    'access_to_internet' : data.access_to_internet,
                                    'ahdaar_card' : data.ahdaar_card,
                                    'pan_card' : data.pan_card,
                                    'ration_card' : data.ration_card,
                                    'driving_license' : data.driving_license,
                                    'id_proof' : data.id_proof,
                                    'photo_id_proof' : data.photo_id_proof,
                                    'access_to_pakka_road' : data.access_to_pakka_road,
                                    'voter_id' : data.voter_id,
                                    'health_id' : data.health_id,
                                    'e_shram_card' : data.e_shram_card,
                                    'access_to_free_and_affordable_health_care' : data.access_to_free_and_affordable_health_care,
                                    'asha_or_anm_worker_providing_healthcare_awareness' : data.asha_or_anm_worker_providing_healthcare_awareness,
                                    'access_to_specialised_doctors' : data.access_to_specialised_doctors,
                                    'employment' : data.employment,
                                    'profession' : data.profession,
                                    'details_of_occupation' : data.details_of_occupation,
                                    'nature_of_income' : data.nature_of_income,
                                    'annual_income' : data.annual_income,
                                    'years_of_service' : data.years_of_service,
                                    } for data in users]            
            return {
                "message": "success",
                'data':serialized_entries,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400
                
    @authenticate
    @api.expect(participant_create_parser)
    @handle_response
    def post(self):
        '''
        API for particpant on boarding
        
        {

        }
        
        '''
        try:
            data = participant_create_parser.parse_args()
            particpant_on_boarding(data)

            return {
                    "message": "success",
                    'data':{},
                    "status": True,
                    "type": "success"
                }, 200
        
        except ZeroDivisionError as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400

class SPOCListAPI(API_Resource):
    @authenticate
    def get(self):
        try:
            fields = ['id', 'name']
            qs = session.query(SPOCMaster).options(
                load_only(*fields)).order_by(SPOCMaster.id).all()
            serialized_entries = [
                {'id': str(record.id), 'spoc_name': record.name} for record in qs]
            return {
                "message": "success",
                'data': serialized_entries,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": f"{str(e)} Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"

            }, 400


# GET Deliverables
class DeliverableByProjectID(API_Resource):
    @authenticate
    def get(self,id):
        try:
            project_obj = get_or_none(ProjectDetailMaster,id)            
            deleverables = session.query(DeliverableDetails).all()
            deliverable_activity_tasks = []
            for deliverable in deleverables:
                delivarable_name = deliverable.name
                activities_id = deliverable.activities
                activity_str = ''
                for activity_id in activities_id:
                    activity_obj = get_or_none(ActivityDetails,activity_id)
                
                
                
            serialized_entries = [
            {'id': str(record.id), 'name': record.name} for record in deleverables]
            return {
                "message": "success",
                'data':serialized_entries,
                "status": True,
                "type": "success"
            }, 200
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400
            
            
class ListDeleverableByProject(API_Resource):
    @authenticate
    def get(self, id):
        try:
            fields = ['id', 'name']
            id = parse_uuid(id, 'project')
            project = session.query(ProjectDetailMaster).filter(
                ProjectDetailMaster.id == id).first()
            if not project:
                return {
                    "message": "project does not exist",
                    "status": False,
                    "type": "custom_error",
                }, 400
            deliverable_ids = project.deliverable
            data = []
            if deliverable_ids:
                for deliverable_id in deliverable_ids:
                    item = ''
                    activity_names = ''
                    task_names = ''
                    deliverable_obj = get_or_none(DeliverableDetails,deliverable_id)
                    deliverable_name = deliverable_obj.name
                    activity_uuids = deliverable_obj.activities
                    data.append({'id':deliverable_id,
                                'value':deliverable_obj.name})
 
                    for actt_uid in activity_uuids:
                        acitivity_obj = get_or_none(ActivityDetails,actt_uid)
                        if acitivity_obj:
                            # activity_names = activity_names + acitivity_obj.name + " ,"
                            activity_names = acitivity_obj.name
                            data.append({'id':actt_uid,
                                'value':activity_names})
                            task_uuids = acitivity_obj.tasks
                            
                            for task_uuid in task_uuids:
                                task_obj = get_or_none(TaskDetails,task_uuid)
                                if task_obj:
                                    # task_names = task_names + task_obj.name + " ,"
                                    task_names = task_obj.name
                                    data.append({'id':task_uuid,
                                    'value':task_names})
                    # activity_names = activity_names[:-1]
                    # task_names = task_names[:-1]
                                # item = f"{deliverable_name} / {activity_names} / {task_names}"
                                # data.append({'id':deliverable_id,
                                #             'value':item})
            res = [i for i in data if not (i['value'] == None)]
            res_updated = res[:]
            if res:
                for i in res:
                    obj = session.query(FormMaster).filter(and_(FormMaster.project==id, FormMaster.is_active==True, FormMaster.deliverables.contains([i['id']]))).first()
                    if obj:
                        res_updated.remove(i)
            return {"message": "success",
                'data':res_updated,
                "status": True,
                "type": "success"
            },200
        except ZeroDivisionError as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400
            
            

def get_form_objects(project_id):
    try:
        form_details = session.query(FormMaster).filter(
                    FormMaster.project == project_id).all()
        return form_details
    except Exception as e:
        print(e)
        session.rollback()
        session.commit()
        return ""
        

class ListOfProjectUserResponse(API_Resource):
    @authenticate
    @api.expect(form_user_response_project_filter)
    def get(self):
        try:
            data = form_user_response_project_filter.parse_args()
            start, end, page_size = parse_pagination_param()
            conditions = []
            if data.project_name:
                project_name = data.project_name.lower()
                conditions.append(func.lower(ProjectDetailMaster.project_name).contains(
                        project_name))
            if conditions:
                projects = session.query(ProjectDetailMaster).filter(or_(*conditions))\
                    .order_by(ProjectDetailMaster.created_at.desc())
            else:
                projects = session.query(ProjectDetailMaster).order_by(ProjectDetailMaster.created_at.desc())
            projects, total_records = project_list_data(projects,start, end)
            try:
                total_pages = math.ceil(total_records / page_size)
            except Exception as e:
                current_app.error_logger.error("validation error", exc_info=e)
                print(str(e))
                total_pages = 0
            project_list = get_project_list(projects,columns = ['id','project_name','state'])
            
            form_project_json = []
            
            for project in project_list:
                forms = get_form_objects(project['id'])
                if forms:
                    for form_data in forms:
                        project['form_id'] = str(form_data.id)
                        project['form_name'] = form_data.form_name
                        project['form_type'] = form_data.type
                        project['form_description'] = form_data.form_description
                        project['participant_details'] = particpant_details(form_data.id)
                        form_project_json.append(project) 
            res_list = [i for n, i in enumerate(form_project_json)
                        if i not in form_project_json[n + 1:]]
            forms = []
            for form in res_list[start:end]:
                forms.append(form)
                                              
            return {
                "message": "success",
                'data': forms,
                "page_size": page_size,
                "total_pages": total_pages,
                "count": total_records,
                "status": True,
                "type": "success"
            }, 200
        except ZeroDivisionError as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400

class ProjectListForParticpant(API_Resource):
    @authenticate
    @api.expect(project_list_participant)
    def get(self):
        try:
            data = project_list_participant.parse_args()
            user_id = parse_uuid(data.get('id'),'participant')
            qs = session.query(UserFormResponse).filter(UserFormResponse.participant_id==user_id).all()
            serialized_entries = []
            for q in qs:
                qa = session.query(ProjectDetailMaster).filter(ProjectDetailMaster.id==q.project).first()
                serialized_entries.append(qa)


            # serialized_entries = [
            #     {'id': str(record.id), 'pro_name': record.project_name} for record in qs]
            serialized_entry=[*set(serialized_entries)]
            serialized_entries = json.loads(
                json.dumps(serialized_entry, cls=AlchemyEncoder)
            )
            return {
                "message": "success",
                'data': serialized_entries,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": f"{str(e)} Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"

            }, 400


class FormDetails(API_Resource):
    @authenticate
    @api.expect(form_details_parser)
    def get(self):
        try:
            data = form_details_parser.parse_args()
            # user_id = parse_uuid(data.get('participant_id'),'participant')
            project_id = parse_uuid(data.get('project_id'), 'project')
            ip_id = data.get('ip_id')
            # mob = data.get('mob')

            if ip_id:
                forms = session.query(FormMaster).filter_by(is_active=True).\
                    filter(FormMaster.project == project_id). \
                    filter(FormMaster.present_status == "published").\
                    filter(FormMaster.type == "custom").\
                    order_by(FormMaster.present_status.desc(), FormMaster.created_at.asc()).all()
                form_list = [i.__dict__ for i in forms]
                for form in forms:
                    responses = session.query(UserFormResponse). \
                        filter_by(is_active=True).filter(UserFormResponse.project == project_id). \
                        filter(UserFormResponse.form == form.id).all()
                    if responses:
                        for resp in responses:
                            if resp.form_response:
                                for i in resp.form_response:
                                    if isinstance(i, dict) and (ip_id in i.values()):
                                        # import pdb;pdb.set_trace()
                                        if (form.__dict__) in form_list:
                                            form_list.remove(form.__dict__)
                                            # continue

                    else:
                        print("no response")

                for json in form_list:
                    if json.get('_sa_instance_state'):
                        json.pop('_sa_instance_state')
                    json['created_at'] = str(json['created_at'])
                    json['updated_at'] = str(json['updated_at'])
                    json['id'] = str(json['id'])
                    if json['modified_by']:
                        json['modified_by'] = str(json['modified_by'])
                    if json['created_by']:
                        json['created_by'] = str(json['created_by'])

            else:
                mob = f"+{data.get('mob').strip()}"
                forms = session.query(FormMaster).filter_by(is_active=True).filter(FormMaster.project == project_id). \
                    filter(FormMaster.present_status == "published").order_by(FormMaster.present_status.desc(),
                                                                              FormMaster.created_at.asc()).all()
                form_list = [i.__dict__ for i in forms]
                for form in forms:
                    responses = session.query(UserFormResponse). \
                        filter_by(is_active=True).filter(UserFormResponse.project == project_id). \
                        filter(UserFormResponse.form == form.id).all()
                    if responses:
                        for resp in responses:
                            if resp.form_response:
                                for i in resp.form_response:
                                    if isinstance(i, dict) and (mob in i.values()):
                                        # import pdb;pdb.set_trace()
                                        if (form.__dict__) in form_list:
                                            form_list.remove(form.__dict__)
                                            # continue

                    else:
                        print("no response")

                # serialized_entries = json.loads(
                #     form_list
                # )
                for json in form_list:
                    if json.get('_sa_instance_state'):
                        json.pop('_sa_instance_state')
                    json['created_at'] = str(json['created_at'])
                    json['updated_at'] = str(json['updated_at'])
                    json['id'] = str(json['id'])
                    if json['modified_by']:
                        json['modified_by'] = str(json['modified_by'])
                    if json['created_by']:
                        json['created_by'] = str(json['created_by'])

            # serialized_entries = serialized_entries[0] if data.get('id') and serialized_entries else serialized_entries

            return {
                "message": "success",
                'data': form_list,
                "status": True,
                "type": "success"
            }, 200
        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": f"{str(e)} Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"

            }, 400


# class FormDetails(API_Resource):
#     @authenticate
#     @api.expect(form_details_parser)
#     def get(self):
#         try:  
#             data = form_details_parser.parse_args() 
#             # user_id = parse_uuid(data.get('participant_id'),'participant')   
#             project_id = parse_uuid(data.get('project_id'),'project')
#             ip_mob = data.get('ip_id_mob')
#             forms = session.query(FormMaster).filter_by(is_active=True).filter(FormMaster.project == project_id).\
#                         filter(FormMaster.present_status == "published").order_by(FormMaster.present_status.desc(), FormMaster.created_at.asc()).all()
#             form_list = forms[:]
#             for form in forms:
#                 responses = session.query(UserFormResponse).\
#                         filter_by(is_active=True).filter(UserFormResponse.project == project_id).\
#                         filter(UserFormResponse.form == form.id).all()
#                 if responses:
#                     for resp in responses:
#                         if resp.form_response:
#                             for i in resp.form_response:
#                                 if isinstance(i, dict) and (ip_mob in i.values()):
#                                     if form in form_list:
#                                         form_list.remove(form)
#                                         break
                                  
#                 else:
#                     print("no response")

#             serialized_entries = json.loads(
#                 json.dumps(form_list, cls=AlchemyEncoder)
#             )

                

#             serialized_entries = serialized_entries[0] if data.get('id') and serialized_entries else serialized_entries
            
#             return {
#                 "message": "success",
#                 'data':serialized_entries,
#                 "status": True,
#                 "type": "success"
#             }, 200
#         except Exception as e:
#             session.rollback()
#             session.commit()
#             print(e)
#             return {
#                 "message": f"{str(e)} Something went wrong, please try after some time",
#                 "status": False,
#                 "type": "custom_error"

#             }, 400

class AllProjectDetails(API_Resource):
    @authenticate
    def get(self):
        try:
            records = []            
            projects = session.query(ProjectDetailMaster).filter(ProjectDetailMaster.is_active==True).\
                order_by(ProjectDetailMaster.created_at.desc())
            
            for pro in projects:
                records.append({'id':str(pro.id),
                                    'project_name':pro.project_name})

            return {
                "message": "success",
                'data': records,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            # current_app.error_logger.error("validation error", exc_info=e)
            return {
                "message": "Something went wrong, please try after some time",
                "data": str(e),
                "status": False,
                "type": "custom_error"
            }, 400

class UnfilledFormProjects(API_Resource):
    @authenticate
    @api.expect(project_search_parser2)
    def get(self):
        try:
            # import time;time.sleep(2)
            data = project_search_parser2.parse_args()
            participant_id = data.get('participant')

            # get all projects the given participants enrolled
            participant_projects = session.query(ProjectDetailMaster).filter(
                ProjectDetailMaster.primary_participants.any(participant_id)
            ).\
                order_by(ProjectDetailMaster.created_at.desc()).all()
            start, end, page_size = parse_project_pagination_params()
            projects = []
            for project in participant_projects:
                forms = session.query(FormMaster).filter(FormMaster.project==project.id).order_by(FormMaster.created_at.desc())
                # case 1
                first_form = forms.first()
                responses = session.query(UserFormResponse).\
                    order_by(UserFormResponse.created_at.desc()).\
                    filter(UserFormResponse.participant_id==participant_id).\
                    filter(UserFormResponse.form==first_form)
                if responses:
                    projects.append(responses.project) 

                # respose_forms=[]
                # for res in responses:
                #     respose_forms.append(res.form)
                #     if res.form==first_form.id:
                #         projects.append(res.project) 
                
                for fm in forms:
                    responses = session.query(UserFormResponse).\
                    order_by(UserFormResponse.created_at.desc()).\
                    filter(UserFormResponse.participant_id==participant_id).\
                    filter(UserFormResponse.form==fm)
                    if not responses:
                        break
                    
                

                            
                
                # case 2              
            project_details, total_records = project_details_data(projects,start, end)
            serialized_entries = json.loads(
                json.dumps(project_details, cls=AlchemyEncoder)
            )
            try:
                total_pages = math.ceil(total_records / page_size)
            except Exception as e:
                current_app.error_logger.error("validation error", exc_info=e)
                print(str(e))
                total_pages = 0
            serialized_entries = serialized_entries[0] if data.get(
                'id') and project_details else serialized_entries

            return {
                "message": "success",
                'data': serialized_entries,
                "page_size": page_size,
                "total_pages": total_pages,
                "count": total_records,
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            # current_app.error_logger.error("validation error", exc_info=e)
            return {
                "message": "Something went wrong, please try after some time",
                "data": str(e),
                "status": False,
                "type": "custom_error"
            }, 400

class BulkParticipantUpload(API_Resource):
    @authenticate
    @api.expect(particpant_bulk_upload_parser)
    def post(self):
        try:
            template = particpant_bulk_upload_parser.parse_args()
            template = template.get('template')

            basicinfo_df = pd.read_excel(template,sheet_name='BasicInformation')
            familyandeducation_df = pd.read_excel(template,sheet_name='FamilyAndEducation')
            address_df = pd.read_excel(template,sheet_name='Address')
            otherdetails_df = pd.read_excel(template,sheet_name='OtherDetails')

            basicinfo_data = json.loads(basicinfo_df.to_json(orient='records'))
            familyandeducation_data = json.loads(familyandeducation_df.to_json(orient='records'))
            address_data = json.loads(address_df.to_json(orient='records'))
            otherdetails_data = json.loads(otherdetails_df.to_json(orient='records'))
            data = []
            length = len(basicinfo_data)
            for l in range(length):
                basic_info = basicinfo_data[l]
                family_details = familyandeducation_data[l]
                address_details = address_data[l]
                other_details = otherdetails_data[l]
                data = {**basic_info, **family_details, **address_details, **other_details}
                validate_field_bulk(data,l)
                particpant_bulk_upload(data)            
           
            return {
                'message':'records inserted successfully',
                'type':'success_message',
                'errors':[],
                'status':True
                },201
    
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400

class StateDetails(API_Resource):
    @authenticate
    @api.expect(state_get_parser)
    def post(self):
        try:            
            data = state_get_parser.parse_args()
            response_deatils = {}            
            state = session.query(StateCity).\
                    filter(StateCity.name==data.state).first()
            if state:
                response_deatils['state']=state.id
            else:
                response_deatils['state']=None

        
            district = session.query(StateCity).\
                    filter(StateCity.name==data.district).first()
            if district:
                response_deatils['district']=district.id
            else:
                response_deatils['district']=None

        
            city = session.query(StateCity).\
                    filter(StateCity.name==data.city).first()
            if city:
                response_deatils['city']=city.id
            else:
                response_deatils['city']=None

            return response_deatils

        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400

class  LocationGetAPI(API_Resource):
    @api.expect(loc_get_parser)
    def post(self):
        try:
            data = loc_get_parser.parse_args()
            place = data.get('place').lower()
            # district = data.get('district').lower()
            # city = data.get('city').lower()
            place = session.query(StateCity).filter(func.lower(StateCity.name)==place).first()
            
            if not place:
                return False
                
            return str(place.id)

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400


            
from sqlalchemy.orm.attributes import flag_modified
import time
class FormUpdateChange(API_Resource):
    def get(self):
        try:  
            # import pdb;pdb.set_trace() 
            count = 0        
            form_response = session.query(UserFormResponse).all()
            for record in form_response:
                count+=1
                print(count)
                if count%1000==0:
                    time.sleep(20)
                processed_data = []
                json_data = record.form_response
                for obj in json_data:
                    if obj['question_name']=='phone' and  obj['answer']=='nan':
                        obj['answer'] = None
                    processed_data.append(obj)
                record.form_response  = processed_data
                flag_modified(record, "form_response")
                session.add(record)
                session.commit()
            return {
                "message": "success",
                'data':[],
                "status": True,
                "type": "success"
            }, 200
        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": f"{str(e)} Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"

            }, 400


class EntrollProjectChecker(API_Resource):
    # @handle_response
    @api.expect(project_enroll_get_parser)
    def get(self):
        try:
            data = project_enroll_get_parser.parse_args()
            ip_id = data.get('ip_id')
            phone = data.get('phone')
            if phone:
                phone = f"+{request.args.get('phone').strip()}"
            response = session.query(UserFormResponse).\
                    filter(UserFormResponse.project==data.project_id).\
                    filter(UserFormResponse.participant_id==data.participant_id).\
                    filter(UserFormResponse.form==data.form_id).all()
            if response:
                return {
                    "message": "Participant already enrolled for this project",
                    "status": False,
                    "type": "data alredy exist"
                }, 406
            else:
                response = session.query(UserFormResponse.form_response). \
                    filter(UserFormResponse.project == data.project_id). \
                    filter(UserFormResponse.form == data.form_id).all()
                data_result = []
                for x in response:
                    if x[0] is not None:
                        if 'formdef_version' in list(x[0][0].keys()):
                            pass
                        elif isinstance(x[0], list):
                            if x[0][0].get('answer') not in ['', None, 'null','nan']:
                                data_result.append(x[0][0].get('answer'))
                            else:
                                data_result.append(x[0][1].get('answer'))
                if ip_id not in  ['null','',None]:
                    if ip_id in data_result:
                        return {
                            "message": "Participant already enrolled for this project",
                            "status": False,
                            "type": "data alredy exist"
                        }, 406
                elif phone not in  ['null','',None]:
                    if phone in data_result:
                        return {
                            "message": "Participant already enrolled for this project",
                            "status": False,
                            "type": "data alredy exist"
                        }, 406
            return {
                "message": "success",
                'data':[],
                "status": True,
                "type": "success"
            }, 200

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": f"{str(e)} Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"

            }, 400


class AreaFocusGoodCSR(API_Resource):
    @api.expect(area_focus_get_parser)
    def post(self):
        try:
            data = area_focus_get_parser.parse_args()
            fields = ['id', 'area_of_focus']
            qs = session.query(AreaFocus).options(
                load_only(*fields)).filter(AreaFocus.id==data['id']).first()
            serialized_entries = {'area_of_focus': qs.area_of_focus}
            return serialized_entries

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": f"{str(e)} Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"

            }, 400


class StateDetailsForGoodcsr(API_Resource):
    @api.expect(goodcsr_state_get_parser)
    def post(self):
        try:            
            data = goodcsr_state_get_parser.parse_args()
            response_deatils = {}            
            place = session.query(StateCity).\
                    filter(StateCity.id==data.id).first()
            if place:
                response_deatils['location']=place.name

            return response_deatils

        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400


class PrimaryParticpantsForGoodCSR(API_Resource):
    @api.expect(particpants_get_parser)
    def post(self):
        try:
            data = particpants_get_parser.parse_args()
            fields = ['id', 'participant_name']
            qs = session.query(PrimaryParticipants).options(
                load_only(*fields)).filter(PrimaryParticipants.id==data['id']).first()
            serialized_entries = {'primary_participants': qs.participant_name}
            return serialized_entries

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": f"{str(e)} Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"

            }, 400


class AreaFocusIDGoodCSR(API_Resource):
    @api.expect(area_focus_id_get_parser)
    def post(self):
        try:
            data = area_focus_id_get_parser.parse_args()
            fields = ['id', 'area_of_focus']
            qs = session.query(AreaFocus).options(
                load_only(*fields)).filter(AreaFocus.area_of_focus==data['name']).first()
            if qs:
                serialized_entries = {'area_of_focus': str(qs.id)}
                return serialized_entries
            return None

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": f"{str(e)} Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"

            }, 400


class StateIDForGoodcsr(API_Resource):
    @api.expect(goodcsr_state_id_get_parser)
    def post(self):
        try:            
            data = goodcsr_state_id_get_parser.parse_args()
            response_deatils = {}            
            place = session.query(StateCity).\
                    filter(StateCity.name==data['name']).first()
            if place:
                response_deatils['id']=place.id
                return response_deatils
            return None

        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": str(e),
                "status": False,
                "type": "custom_error"
            }, 400


class PrimaryParticpantsIDForGoodCSR(API_Resource):
    @api.expect(particpants_id_get_parser)
    def post(self):
        try:
            data = particpants_id_get_parser.parse_args()
            fields = ['id', 'participant_name']
            qs = session.query(PrimaryParticipants).options(
                load_only(*fields)).filter(PrimaryParticipants.participant_name==data['name']).first()
            if qs:
                serialized_entries = {'primary_participants': str(qs.id)}
                return serialized_entries
            
            return None

        except Exception as e:
            session.rollback()
            session.commit()
            print(e)
            return {
                "message": f"{str(e)} Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"

            }, 400

class UnfilledFormsForSurveyCto(API_Resource):
    @authenticate
    @api.expect(unfilled_forms_get_parser)
    def get(self):
        data = unfilled_forms_get_parser.parse_args()
        ip_id = data.get('ip_id')
        phone = data.get('phone')
        participant_id = data.get('participant_id')
        project_id = data.get('project_id')
        try:
            forms = session.query(FormMaster).\
                    filter(FormMaster.project==project_id).\
                    filter(FormMaster.is_active==True).\
                    filter(FormMaster.present_status=='published').\
                    filter(FormMaster.type=='survey_cto_form').\
                    all()
            forms_copy = forms
            if forms:
                for form in forms:
                    responses = session.query(UserFormResponse).\
                            filter(UserFormResponse.form==form.id).\
                            filter(UserFormResponse.project==project_id).\
                            all()
                    if responses:
                        for resp in responses:
                            if resp.form_response_type == 'survey_cto_form_single':
                                if resp.participant_id == participant_id:
                                    forms_copy.remove(form)
                            else:
                                for res in resp.form_response:
                                    if (
                                        ip_id not in ['null', None, '']
                                        and ip_id in res.values()
                                        or ip_id in ['null', None, '']
                                        and phone in res.values()
                                    ):
                                        forms_copy.remove(form)

            result = json.loads(json.dumps(forms_copy, cls=AlchemyEncoder))

            return {
                "message": "Unfilled Forms fetched successfully",
                "status": True,
                "data": result
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
        

class OccupationAPI(API_Resource):
    @api.expect(occupationparser)
    def get(self):
        try:
            data = occupationparser.parse_args()
            occupation_id = str(data.get("occupation_id")) if data.get("occupation_id") else ''
            fields = ['id', 'name']
            data = []
            if not occupation_id:
                qs = session.query(Occupation).options(load_only(
                    *fields)).filter(Occupation.lookup_id == None).filter(Occupation.is_active == True).order_by(Occupation.id).all()
                occupation_entries = [
                    {'id': str(record.id), 'name': record.name} for record in qs]
                return {
                "message": "success",
                'data' : occupation_entries,
                "status": True,
                "type": "success"
            }, 200

            qs = session.query(Occupation).options(load_only(
                *fields)).filter(Occupation.lookup_id.in_([occupation_id])).filter(Occupation.is_active == True).order_by(Occupation.name).all()
            for record in qs:
                sub_occupation_entries ={'id': str(record.id), 'name': record.name}               

                qd = session.query(Occupation).options(load_only(
                    *fields)).filter(Occupation.lookup_id.in_([str(record.id)])).filter(Occupation.is_active == True).order_by(Occupation.name).all()
                for record in qd: 
                    sub_occupation_entries['project_name'] = record.name
                    
                data.append(sub_occupation_entries)
            return {
                "message": "success",
                'data': data,
                "status": True,
                "type": "success"
            }, 200
        except Exception as e:
            session.rollback()
            session.commit()
            return {
                "message": "Something went wrong, please try after some time",
                "status": False,
                "type": "custom_error"
            }, 400