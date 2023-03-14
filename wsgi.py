from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from skilling_pathway.api.app import create_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = create_app(static_path=os.path.abspath(os.path.dirname("upload/")))
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = os.path.abspath(os.path.dirname("upload/"))
db = SQLAlchemy(app, engine_options={"pool_pre_ping": True})
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)



@app.route('/')
def hello():
    return "Hello World!"


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
