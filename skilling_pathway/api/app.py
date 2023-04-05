from flask import Flask
from flask_cors import CORS
# from flask_jwt_extended import JWTManager
from .v1 import v1_blueprint
from .v2 import v2_blueprint
import os
from .extensions import celery, client


s = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def make_celery(app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def setup_mongo():
    return client

def create_app(static_path=None):
    app = Flask(__name__,static_folder=static_path)
    make_celery(app)
    CORS(app)
    setup_mongo()
    app.config["MONGO_DB"] = client
    # Setup the Flask-JWT-Extended extension
    # app.config["JWT_SECRET_KEY"] = "hbdbd6726hlooaqw3343ncn"  # Change this!
    # jwt = JWTManager(app)


    @app.errorhandler(404)
    def page_not_found(error):
        return {"message": "Requested resource does not exist"}, 404

    @app.errorhandler(ValueError)
    def error_500(error):
        return {"message": "Internal server error"}, 500

    app.register_blueprint(v1_blueprint,url_prefix='/v1/')
    app.register_blueprint(v2_blueprint)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
