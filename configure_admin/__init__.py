from flask_admin.contrib.sqla import ModelView

from spark.models.auth.auth import (
    User
)

# from skilling_pathway.models.project import MaritalStatus2


def register_model(admin, db):
    # register models
    # admin.add_view(ModelView(MaritalStatus, db.session))
    

    return admin
