from flask import Blueprint
from flask_restx import Api
from skilling_pathway.api.v1.resources.course.course import (
                                                    CourseList,CourseByID,
                                                    CourseListNew,CourseContentAPI
)
from skilling_pathway.api.v1.resources.resume_builder.resume_builder import (ResumeBuilderAPI,
                                                                             UploadResume, ComprehentResume, TextractResume,
                                                                             TextractPdfResume)
from skilling_pathway.api.v1.resources.course.course import CourseList,CourseByID,CourseGrantAPI,CourseGrantDashboardAPI,CoursesByCategoryAPI,CourseGrantCheckAPI
from skilling_pathway.api.v1.resources.profile.profile import ProfileCreateUpdateAPI,ProfileGetAPI,ProfileAPI,ProfileResumeUpdateApi,ProfileStatusUpdateAPI                                                             
from skilling_pathway.api.v1.resources.profile.api import GetCertificate,GetCourseTags,CourseTagsList

v1_blueprint = Blueprint(name="v1", import_name=__name__)
v1_api = Api(app=v1_blueprint, prefix="/",doc='/apidocs/')

# course api's
v1_api.add_resource(CourseList,'/course/list/')
v1_api.add_resource(CourseByID,'/course/<id>/')
v1_api.add_resource(CourseListNew,'/course/list/new/')
v1_api.add_resource(CourseContentAPI,'/course_content/<id>/')
v1_api.add_resource(CourseGrantAPI,'/course/grant/')
v1_api.add_resource(CourseGrantCheckAPI,'/course/grant/check/')
v1_api.add_resource(CourseGrantDashboardAPI,'/course/grant/dashboard')
v1_api.add_resource(CoursesByCategoryAPI,'/courses/list/by_category/')
v1_api.add_resource(GetCertificate,'/get_certificate/')
v1_api.add_resource(GetCourseTags,'/get_course_tags')
v1_api.add_resource(CourseTagsList,'/tag_list/')


# profile api's
v1_api.add_resource(ProfileCreateUpdateAPI, '/profile/create_update/')
v1_api.add_resource(ProfileGetAPI, '/profile/<participant_id>/')
v1_api.add_resource(ProfileAPI, '/profile/')
v1_api.add_resource(ProfileResumeUpdateApi, '/profile/update/resume/<id>/')
v1_api.add_resource(ProfileStatusUpdateAPI, '/profile/status_update/<profile_id>/')

v1_api.add_resource(ResumeBuilderAPI,'/resume-builder/')
v1_api.add_resource(UploadResume,'/resume-upload/')


v1_api.add_resource(ComprehentResume,'/comprehent/resume-upload/')
v1_api.add_resource(TextractResume,'/textract/resume-upload/')
v1_api.add_resource(TextractPdfResume,'/resume_parser/textract')

