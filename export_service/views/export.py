"""Export routes."""  # pylint: disable=cyclic-import
import uuid
from datetime import datetime
from flask import request
from flask_api import status
from flask_restful import Resource
import requests
from export_service.serializers.export_schema import ExportInputSchema
from export_service import APP
from export_service.config.base_config import Config
from export_service.rabbitmq_setup import CHANNEL

SCHEMA = ExportInputSchema()
AUTH_TOKEN_KEY = 'auth_token'


class Export(Resource):
    """Export."""
    def post(self):
        """ get parameters and form a task.
        :return: str: message
        :raise: 404 Error: if no parameters, or if parameters are with an incorrect type
        """
        task_dict = {}

        errors = SCHEMA.validate(request.json)
        if errors:
            APP.logger.error(errors)
            return errors, status.HTTP_400_BAD_REQUEST

        request_data = request.get_json()

        # task_id
        task_dict['task_id'] = uuid.uuid4().int

        # form_id
        try:
            url = Config.FORM_SERVICE_URL + f"/{request_data['form_id']}"
            response = requests.get(url=url)
        except requests.exceptions.ConnectionError:
            response_obj = {
                "error": "Can't connect to form-service."
            }
            APP.logger.error(response_obj)
            return response_obj, status.HTTP_500_INTERNAL_SERVER_ERROR

        if response.status_code == 500:
            response_obj = {
                "error": "Internal error at form-service."
            }
            APP.logger.error(response_obj)
            return response_obj, status.HTTP_500_INTERNAL_SERVER_ERROR

        elif response.status_code == 404:
            response_obj = {
                "error": f"The form with id {request_data['form_id']} does not exist."
            }
            APP.logger.error(response_obj)
            return response_obj, status.HTTP_400_BAD_REQUEST

        elif response.status_code == 200:
            task_dict['form_id'] = request_data['form_id']

        # groups
        try:
            groups = request_data['groups']
        except KeyError:
            groups = []

        try:
            url = Config.GROUPS_SERVICE_URL
            response = requests.get(url=url)
        except requests.exceptions.ConnectionError:
            response_obj = {
                "error": "Can't connect to groups-service."
            }
            APP.logger.error(response_obj)
            return response_obj, status.HTTP_500_INTERNAL_SERVER_ERROR

        if response.status_code == 500:
            response_obj = {
                "error": "Internal error at groups-service."
            }
            APP.logger.error(response_obj)
            return response_obj, status.HTTP_500_INTERNAL_SERVER_ERROR

        groups_do_not_exist = []
        for group in groups:
            response = requests.get(url=url+f"/{group}")
            if response.status_code == 404:
                groups_do_not_exist.append(group)

        if groups_do_not_exist:
            if len(groups_do_not_exist) == 1:
                response_obj = {
                    "error": f"Group {groups_do_not_exist[0]} does not exist."
                }
            else:
                response_obj = {
                    "error": f"Groups {', '.join(str(group) for group in groups_do_not_exist)} "
                             f"don't exist."
                }
            APP.logger.error(response_obj)
            return response_obj, status.HTTP_400_BAD_REQUEST

        groups_not_assigned_to_form = []
        for group in groups:
            response = requests.get(url=url+f"/{group}")
            if request_data['form_id'] not in response.json()['assigned_to_forms']:
                groups_not_assigned_to_form.append(group)

        if groups_not_assigned_to_form:
            if len(groups_not_assigned_to_form) == 1:
                response_obj = {
                    "error": f"Group {groups_not_assigned_to_form[0]} is not assigned to "
                             f"form {request_data['form_id']}."
                }
            else:
                response_obj = {
                    "error": f"Groups "
                             f"{', '.join(str(group) for group in groups_not_assigned_to_form)}"
                             f" are not assigned to form {request_data['form_id']}."
                }
            APP.logger.error(response_obj)
            return response_obj, status.HTTP_400_BAD_REQUEST

        task_dict['groups'] = groups

        # export_format
        task_dict['export_format'] = request_data['export_format']

        # email
        url = Config.USERS_SERVICE_URL + "/profile"
        cookies = request.cookies
        try:
            response = requests.get(url=url, cookies=cookies)
        except requests.exceptions.ConnectionError:
            response_obj = {
                "error": "Can't connect to users-service."
            }
            APP.logger.error(response_obj)
            return response_obj, status.HTTP_500_INTERNAL_SERVER_ERROR

        try:
            task_dict['email'] = response.json()['email']
        except KeyError:
            response_obj = {
                "error": "Signature expired. Please, log in again."
            }
            APP.logger.error(response_obj)
            return response_obj, status.HTTP_403_FORBIDDEN

        # from_date
        try:
            if not request_data['from_date'] and request_data['from_date'] == request_data['to_date']:  # pylint: disable=line-too-long
                from_date = datetime.strptime(request_data['from_date'], "%Y-%m-%d")
                new_day = from_date.day - 1
                from_date = from_date.replace(day=new_day)
                from_date = str(from_date.date())
                task_dict['from_date'] = from_date
            else:
                task_dict['from_date'] = request_data['from_date']
        except KeyError:
            pass

        # to_date
        try:
            task_dict['to_date'] = request_data['to_date']
        except KeyError:
            pass

        CHANNEL.basic_publish(exchange='',
                              routing_key='export',
                              body=str(task_dict))

        return "Task successfully sent to worker-service."
