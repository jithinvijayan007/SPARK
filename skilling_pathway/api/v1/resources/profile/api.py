from flask import jsonify
from skilling_pathway.api.v1.resources.profile.main import callCursor,GetCertificateForParticipant,GetCousreTags
from skilling_pathway.api.v1.resources.Resource import API_Resource, NameSpace 
import json
from .parser_helper import (certificate_post_parser,
)

api = NameSpace("tags")


class GetCertificate(API_Resource):
    @api.expect(certificate_post_parser)
    def post(self):
        data = certificate_post_parser.parse_args()
        user = data.get('user_name')
        result = GetCertificateForParticipant(user).get_certificate_for_participant()
        return jsonify(json.loads(result))


class GetCourseTags(API_Resource):
    def get(self):
        result = GetCousreTags().get_course_tags()
        return jsonify(json.loads(result))


