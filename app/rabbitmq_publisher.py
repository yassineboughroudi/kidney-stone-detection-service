import pika
import json
from app.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_EXCHANGE

def publish_event(event: dict):
    """
    Publish an event to RabbitMQ.
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    )
    channel = connection.channel()

    # Declare the exchange
    channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type="fanout")

    # Publish the message
    channel.basic_publish(
        exchange=RABBITMQ_EXCHANGE,
        routing_key="",
        body=json.dumps(event),
    )

    connection.close()
