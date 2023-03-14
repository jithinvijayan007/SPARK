from flask_admin.contrib.sqla import ModelView

from skilling_pathway.models.form.form import (
    MaritalStatus,
   MaritalStatus1
)

from skilling_pathway.models.project import MaritalStatus2


def register_model(admin, db):
    # register models
    admin.add_view(ModelView(MaritalStatus, db.session))
    admin.add_view(ModelView(MaritalStatus1, db.session))
    admin.add_view(ModelView(MaritalStatus2, db.session))
    

    return admin
