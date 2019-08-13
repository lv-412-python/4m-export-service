"""RabbitMQ Config."""
import pika

RABBITMQ_HOST = "rabbitmq"
RABBITMQ_PORT = 5672

CONNECTION = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, heartbeat=0)
)
CHANNEL = CONNECTION.channel()

CHANNEL.queue_declare(queue="export")
