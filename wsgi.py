from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from skilling_pathway.api.app import create_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = create_app()
app.config.from_object(os.environ["APP_SETTINGS"])
app.config["DATABASE_URL"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.abspath(os.path.dirname("upload/"))
app.config["SQLALCHEMY_POOL_RECYCLE"] = 45

db = SQLAlchemy(app, engine_options={"pool_pre_ping": True})
migrate = Migrate(app, db, compare_type=True)
# configure_exporter()


manager = Manager(app)
manager.add_command("db", MigrateCommand)


# admin views
# admin = Admin(app, name="Appreciate master")
# admin = register_model(admin, db)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/<name>")
def hello_name(name):
    return "Hello {}!".format(name)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=6000)
