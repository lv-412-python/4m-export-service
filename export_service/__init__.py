"""Init export service."""
from flask import Flask
from flask_restful import Api
from flask_cors import CORS


APP = Flask(__name__)
CORS(APP)
API = Api(APP)

# from export_service.views.export import export  #pylint: disable=wrong-import-position
from export_service.views import resources
