"""Export routes."""  # pylint: disable=cyclic-import
from flask import request, abort
from flask_restful import Resource
import pika


class Export(Resource):
    """Export."""
    def post(self):  # pylint: disable=no-self-use
        """ get parameters and form a task
        :return: str: message
        :raise: 404 Error: if no parameters, or if parameters are with an incorrect type
        """
        try:
            form_id = request.form.get('form_id', type=int)
            if request.form.get('groups', type=str):
                groups = [int(x) for x in (request.form.get('groups', type=str)).split(',')]
            else:
                groups = []
            export_format = request.form.get('format')
            if form_id is None or export_format not in ('pdf', 'csv', 'xls'):
                raise ValueError
        except (AttributeError, ValueError):
            abort(400)

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
