import pika
import json
import logging
from app.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_EXCHANGE

def publish_event(event_data):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
        )
        channel = connection.channel()

        # Declare the queue to ensure it exists
        channel.queue_declare(queue='notification.queue')

        message = json.dumps(event_data)
        channel.basic_publish(
            exchange='',  # Default exchange
            routing_key='notification.queue',  # Directly send to the queue
            body=message
        )

        logging.info(f"Published event to RabbitMQ: {message}")
        connection.close()

    except Exception as e:
        logging.error(f"Failed to publish event: {str(e)}")
