"""Init export service."""
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt


APP = Flask(__name__)
CORS(APP)
APP.secret_key = 'very_secret'
API = Api(APP)
JWT = JWTManager(APP)
BCRYPT = Bcrypt(APP)

# from export_service.views.export import export  #pylint: disable=wrong-import-position
from export_service.views import resources
