from flask import Blueprint
from flask_restx import Api
from skilling_pathway.api.v1.resources.course.course import CourseList,CourseByID
from skilling_pathway.api.v1.resources.resume_builder.resume_builder import ResumeBuilder


v1_blueprint = Blueprint(name="v1", import_name=__name__)
v1_api = Api(app=v1_blueprint, prefix="/",doc='/apidocs/')

v1_api.add_resource(CourseList,'/course/list/')
v1_api.add_resource(CourseByID,'/course/<id>/')
v1_api.add_resource(ResumeBuilder,'/resume-builder/')