from flask import Blueprint
from flask_restx import Api
from skilling_pathway.api.v1.resources.course.course import (
                                                    CourseList,CourseByID,
                                                    CourseListNew,CourseContentAPI
)
from skilling_pathway.api.v1.resources.resume_builder.resume_builder import (ResumeBuilderAPI,
                                                                             UploadResume)
from skilling_pathway.api.v1.resources.course.course import CourseList,CourseByID
from skilling_pathway.api.v1.resources.profile.profile import ProfileCreateUpdateAPI,ProfileGetAPI,ProfileAPI


v1_blueprint = Blueprint(name="v1", import_name=__name__)
v1_api = Api(app=v1_blueprint, prefix="/",doc='/apidocs/')

# course api's
v1_api.add_resource(CourseList,'/course/list/')
v1_api.add_resource(CourseByID,'/course/<id>/')
v1_api.add_resource(CourseListNew,'/course/list/new/')
v1_api.add_resource(CourseContentAPI,'/course_content/<id>/')

# profile api's
v1_api.add_resource(ProfileCreateUpdateAPI, '/profile/create_update/')
v1_api.add_resource(ProfileGetAPI, '/profile/<participant_id>/')
v1_api.add_resource(ProfileAPI, '/profile/')

v1_api.add_resource(ResumeBuilderAPI,'/resume-builder/')
v1_api.add_resource(UploadResume,'/resume-upload/')


