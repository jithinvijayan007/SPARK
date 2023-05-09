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

profile_update_parser = reqparse.RequestParser()
profile_update_parser.add_argument(
    'access-token',type=str,location='headers',required=True,
)
profile_update_parser.add_argument(
    "profile_id", type=str, required=True
)