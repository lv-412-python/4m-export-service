"""Export routes."""  # pylint: disable=cyclic-import
from flask import request
from flask_api import status
from flask_restful import Resource
import pika
from export_service.serializers.export_schema import ExportInputSchema

SCHEMA = ExportInputSchema()


class Export(Resource):
    """Export."""
    def post(self):  # pylint: disable=no-self-use
        """ get parameters and form a task.
        :return: str: message
        :raise: 404 Error: if no parameters, or if parameters are with an incorrect type
        """
        errors = SCHEMA.validate(request.json)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST

        req_data = request.get_json()

        form_id = req_data['form_id']
        groups = [] if not req_data['groups'] else req_data['groups']
        export_format = req_data['export_format']

        task = {
            'form_id': form_id,
            'groups': groups,
            'format': export_format
        }

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='export')
        channel.basic_publish(exchange='',
                              routing_key='export',
                              body=str(task))

        connection.close()
        return "Task successfully sent to worker-service."
