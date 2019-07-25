"""Export routes."""  # pylint: disable=cyclic-import
import uuid
from datetime import datetime
from flask import request, session
from flask_jwt_extended import decode_token
from flask_api import status
from flask_restful import Resource
import pika
from jwt.exceptions import ExpiredSignatureError
from export_service.serializers.export_schema import ExportInputSchema
from export_service import APP

SCHEMA = ExportInputSchema()
AUTH_TOKEN_KEY = 'auth_token'


class Export(Resource):
    """Export."""
    def post(self):  #pylint: disable=too-many-locals
        """ get parameters and form a task.
        :return: str: message
        :raise: 404 Error: if no parameters, or if parameters are with an incorrect type
        """
        errors = SCHEMA.validate(request.json)
        if errors:
            APP.logger.error(errors)
            return errors, status.HTTP_400_BAD_REQUEST

        req_data = request.get_json()

        task_id = uuid.uuid4().int
        form_id = req_data['form_id']
        export_format = req_data['export_format']

        try:
            groups = req_data['groups']
        except KeyError:
            groups = []

        task = {
            'task_id': task_id,
            'form_id': form_id,
            'groups': groups,
            'export_format': export_format
        }

        try:
            if not req_data['from_date'] and req_data['from_date'] == req_data['to_date']:
                from_date = datetime.strptime(req_data['from_date'], "%Y-%m-%d")
                new_day = from_date.day - 1
                from_date = from_date.replace(day=new_day)
                from_date = str(from_date.date())
                task['from_date'] = from_date
            else:
                task['from_date'] = req_data['from_date']
        except KeyError:
            pass

        try:
            task['to_date'] = req_data['to_date']
        except KeyError:
            pass

        try:
            access_token = session[AUTH_TOKEN_KEY]
        except KeyError as err:
            APP.logger.error(err.args)
            response_obj = {
                'error': 'Provide a valid auth token.'
            }
            return response_obj, status.HTTP_403_FORBIDDEN
        try:
            user_info = decode_token(access_token, allow_expired=True)
            task['user_email'] = user_info['identity']
        except ExpiredSignatureError as err:
            APP.logger.error(err.args)
            response_obj = {
                'error': 'Signature expired. Please, log in again.'
            }
            return response_obj, status.HTTP_403_FORBIDDEN

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq',
                                                                       port=5672))
        channel = connection.channel()
        channel.queue_declare(queue='export')
        channel.basic_publish(exchange='',
                              routing_key='export',
                              body=str(task))

        connection.close()
        return "Task successfully sent to worker-service."
