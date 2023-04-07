from datetime import datetime
from flask_restx import reqparse
import werkzeug

resume_builder_parser = reqparse.RequestParser()
resume_builder_parser.add_argument(
    'access-token',type=str,location='headers',required=True,
)
resume_builder_parser.add_argument('full_name',type=str,location='json')
resume_builder_parser.add_argument('mobile',type=str,location='json')
resume_builder_parser.add_argument('email',type=str,location='json')
resume_builder_parser.add_argument('gender',choices=('male','female','others'),type=str,location='json')
resume_builder_parser.add_argument('current_address',type=str,location='json')
resume_builder_parser.add_argument('educational_qualification',type=list,location='json')
resume_builder_parser.add_argument('skills',type=list,location='json')
resume_builder_parser.add_argument('work_experiance',type=list,location='json')
resume_builder_parser.add_argument('certifications',type=list,location='json')


# Upload Resume and Parser
resume_parser = reqparse.RequestParser()
resume_parser.add_argument(
    'access-token',type=str,location='headers',required=True,
)
resume_parser.add_argument('resume',type=str,location='files')


# Filter Resume
resume_filter_parser = reqparse.RequestParser()
resume_filter_parser.add_argument(
    'access-token',type=str,location='headers',required=True,
)
resume_filter_parser.add_argument('id',type=str, required=False)