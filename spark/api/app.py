from flask import Flask
from flask_cors import CORS
# from flask_jwt_extended import JWTManager
from .v1 import v1_blueprint
import os
from flask_jwt_extended import JWTManager



s = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def create_app(static_path=None):
    app = Flask(__name__,static_folder=static_path)
    CORS(app)
    # Setup the Flask-JWT-Extended extension
    app.config["JWT_SECRET_KEY"] = "hbdbd6726hlooaqw3343ncn"  # Change this!
    jwt = JWTManager(app)


    @app.errorhandler(404)
    def page_not_found(error):
        return {"message": "Requested resource does not exist"}, 404

    @app.errorhandler(ValueError)
    def error_500(error):
        return {"message": "Internal server error"}, 500

    app.register_blueprint(v1_blueprint,url_prefix='/v1/')

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
