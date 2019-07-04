"""export routes"""  # pylint: disable=cyclic-import
from flask import request, abort
import pika
from export_service import APP


@APP.route('/api/export/')
def export():
    """export route"""
    try:
        form_id = request.args.get('form_id', type=int)
        if request.args.get('groups', type=str):
            groups = [int(x) for x in (request.args.get('groups', type=str)).split(',')]
        else:
            groups = []
        export_format = request.args.get('format')
        if form_id is None or export_format is None or export_format not in ('pdf', 'csv', 'xls'):
            raise ValueError
    except (AttributeError, ValueError):
        abort(400)

    task = {'form_id': form_id,
            'groups': groups,
            'format': export_format}

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='export')
    channel.basic_publish(exchange='',
                          routing_key='export',
                          body=str(task))

    channel.queue_declare(queue='answer_to_export')
    for method_frame, properties, body in channel.consume('answer_to_export'):  # pylint: disable=unused-variable
        msg = body
        if method_frame.delivery_tag == 1:
            break

    connection.close()
    return msg
