from flask_admin.contrib.sqla import ModelView

from skilling_pathway.models.course.course import (
    MaritalStatus,
   MaritalStatus1
)

# from skilling_pathway.models.project import MaritalStatus2


def register_model(admin, db):
    # register models
    # admin.add_view(ModelView(MaritalStatus, db.session))
    

    return admin
