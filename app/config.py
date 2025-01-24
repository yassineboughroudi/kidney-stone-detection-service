from decouple import config

# Load service-related configurations
SERVICE_NAME = config("SERVICE_NAME", default="kidney-stone-service")
RABBITMQ_HOST = config("RABBITMQ_HOST", default="localhost")
RABBITMQ_PORT = config("RABBITMQ_PORT", cast=int, default=15672)
RABBITMQ_EXCHANGE = config("RABBITMQ_EXCHANGE", default="predictions")
