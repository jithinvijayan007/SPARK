from flask_restx import reqparse

profile_create_update_parser = reqparse.RequestParser()
profile_create_update_parser.add_argument(
    "access-token", type=str, required=True, location="headers"
)
profile_create_update_parser.add_argument(
    "participant_id", type=str, location="form", required=True
)
profile_create_update_parser.add_argument(
    "form_response", type=str, location="form", required=True
)


participant_profile_get_parser = reqparse.RequestParser()
participant_profile_get_parser.add_argument(
    "access-token", type=str, required=True, location="headers"
)

profile_update_resume_parser = reqparse.RequestParser()
profile_update_resume_parser.add_argument(
    'access-token',type=str,location='headers',required=True,
)
profile_update_resume_parser.add_argument('other_languages',type=str,location='json')
profile_update_resume_parser.add_argument('current_skills',type=str,location='json')
profile_update_resume_parser.add_argument('interested_course',type=str,location='json')
profile_update_resume_parser.add_argument('educational_qualifications',type=str,location='json')
profile_update_resume_parser.add_argument('address',type=str,location='json')
profile_update_resume_parser.add_argument('email',type=str,location='json')
profile_update_resume_parser.add_argument('mobile',type=str,location='json')
profile_update_resume_parser.add_argument('gender',choices=('male','female','others'),type=str,location='json')
profile_update_resume_parser.add_argument('certificates',type=str,location='json')
profile_update_resume_parser.add_argument('experience',type=str,location='json')

profile_status_update_parser = reqparse.RequestParser()
profile_status_update_parser.add_argument(
    'access-token',type=str,location='headers',required=True,
)

certificate_post_parser = reqparse.RequestParser()
certificate_post_parser.add_argument(
    "user_name", type=str, required=True
)

profile_update_parser = reqparse.RequestParser()
profile_update_parser.add_argument(
    'access-token',type=str,location='headers',required=True,
)
profile_update_parser.add_argument('other_languages',type=str,location='json')
profile_update_parser.add_argument('current_skills',type=str,location='json')
profile_update_parser.add_argument('interested_course',type=str,location='json')
profile_update_parser.add_argument('educational_qualifications',type=str,location='json')
profile_update_parser.add_argument('address',type=str,location='json')
profile_update_parser.add_argument('summary',type=str,location='json')
# profile_update_parser.add_argument('email',type=str,location='json')
# profile_update_parser.add_argument('mobile',type=str,location='json')
profile_update_parser.add_argument('gender',choices=('male','female','others'),type=str,location='json')
profile_update_parser.add_argument('experience',type=str,location='json')
profile_update_parser.add_argument('summary',type=str,location='json')
profile_update_parser.add_argument('highest_education',type=str,location='json')
profile_update_parser.add_argument('preferred_course_language',type=str,location='json')
profile_update_parser.add_argument('preferred_employment_type',type=str,location='json')
profile_update_parser.add_argument('preferred_job_location_city',type=str,location='json')
profile_update_parser.add_argument('preferred_job_location_state',type=str,location='json')
profile_update_parser.add_argument('preferred_job_role',type=str,location='json')
profile_update_parser.add_argument('preferred_work_place_type',type=str,location='json')
profile_update_parser.add_argument('current_employment_details',type=str,location='json')
profile_update_parser.add_argument('employment_start_date',type=str,location='json')
profile_update_parser.add_argument('employment_end_date',type=str,location='json')