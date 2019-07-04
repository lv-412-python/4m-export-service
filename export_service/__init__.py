"""Init export service"""
from flask import Flask


APP = Flask(__name__)

from export_service.views.export import export  #pylint: disable=wrong-import-position
