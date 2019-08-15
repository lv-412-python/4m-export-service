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


def check_authority(view):
    """Decorator for resources"""
    def func_wrapper(*args, **kwargs):
        """wrapper"""
        if request.cookies['admin'] == 'False' and request.method != 'GET':
            return {"error": "Forbidden."}, status.HTTP_403_FORBIDDEN
        return view(*args, **kwargs)
    return func_wrapper


class Export(Resource):
    """Export."""

    @check_authority
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
        form_id = _get_form_id(request_data)
        if not isinstance(form_id, int):
            return form_id
        task_dict['form_id'] = form_id

        # groups
        groups = _get_groups(request_data)
        if not isinstance(groups, list):
            return groups
        task_dict['group_id'] = groups

        # export_format
        task_dict['export_format'] = request_data['export_format']

        # email
        user_email = _get_user_email()
        if not isinstance(user_email, str):
            return user_email
        task_dict['email'] = user_email

        # from_date
        from_date = _get_from_date(request_data)
        if isinstance(from_date, str):
            task_dict['from_date'] = from_date

        # to_date
        try:
            task_dict['to_date'] = request_data['to_date']
        except KeyError:
            pass

        CHANNEL.basic_publish(exchange='',
                              routing_key='export',
                              body=str(task_dict))

        return "Task successfully sent to worker-service."


def _get_form_id(request_data):
    url = Config.FORM_SERVICE_URL + f"/{request_data['form_id']}"
    try:
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

    if response.status_code == 404:
        response_obj = {
            "error": f"The form with id {request_data['form_id']} does not exist."
        }
        APP.logger.error(response_obj)
        return response_obj, status.HTTP_400_BAD_REQUEST

    return request_data['form_id']


def _get_groups(request_data):
    try:
        groups = request_data['groups']
    except KeyError:
        return []

    try:
        url = Config.GROUPS_SERVICE_URL
        response = requests.get(url=url+"/1")
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

    groups = _if_groups_exist(url, groups)
    if not isinstance(groups, list):
        return groups

    groups = _if_groups_assigned_to_form(url, groups, request_data)
    if not isinstance(groups, list):
        return groups

    groups = _if_groups_answered_form(request_data, groups)

    return groups


def _if_groups_exist(url, groups):
    groups_do_not_exist = []
    for group in groups:
        response = requests.get(url=url + f"/{group}")
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
    return groups


def _if_groups_assigned_to_form(url, groups, request_data):
    groups_not_assigned_to_form = []
    for group in groups:
        response = requests.get(url=url + f"/{group}")
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
    return groups


def _if_groups_answered_form(request_data, groups):

    url = Config.ANSWERS_SERVICE_URL + f"?form_id={request_data['form_id']}"
    try:
        response = requests.get(url=url)
    except requests.exceptions.ConnectionError:
        response_obj = {
            "error": "Can't connect to answers-service."
        }
        APP.logger.error(response_obj)
        return response_obj, status.HTTP_500_INTERNAL_SERVER_ERROR

    if response.status_code == 500:
        response_obj = {
            "error": "Internal error at answers-service."
        }
        APP.logger.error(response_obj)
        return response_obj, status.HTTP_500_INTERNAL_SERVER_ERROR

    groups_did_not_answer_form = []

    for group in groups:
        response = requests.get(url=url+f"&group_id={group}")
        print(response)
        if response.status_code == 404:
            groups_did_not_answer_form.append(group)

    if groups_did_not_answer_form:
        if len(groups_did_not_answer_form) == 1:
            response_obj = {
                "error": f"Group {groups_did_not_answer_form[0]} did not fill in "
                         f"the form {request_data['form_id']}."
            }
        else:
            response_obj = {
                "error": f"Groups {', '.join(str(group) for group in groups_did_not_answer_form)}"
                         f" did not fill in the form {request_data['form_id']}."
            }
        APP.logger.error(response_obj)
        return response_obj, status.HTTP_400_BAD_REQUEST

    return groups


def _get_user_email():
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
        return response.json()['email']
    except KeyError:
        response_obj = {
            "error": "Signature expired. Please, log in again."
        }
        APP.logger.error(response_obj)
        return response_obj, status.HTTP_403_FORBIDDEN


def _get_from_date(request_data):
    try:
        if request_data['from_date'] == request_data['to_date']:
            from_date = datetime.strptime(request_data['from_date'], "%Y-%m-%d")
            new_day = from_date.day - 1
            from_date = from_date.replace(day=new_day)
            from_date = str(from_date.date())
            return from_date
        return request_data['from_date']
    except KeyError:
        pass
