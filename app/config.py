from decouple import config

# Load service-related configurations
SERVICE_NAME = config("SERVICE_NAME", default="kidney-stone-service")
RABBITMQ_HOST = config("RABBITMQ_HOST", default="rabbitmq")  # Use Docker container name
RABBITMQ_PORT = config("RABBITMQ_PORT", cast=int, default=15672)
RABBITMQ_EXCHANGE = config("RABBITMQ_EXCHANGE", default="predictions")

# MongoDB-related configurations
MONGODB_URI = config("MONGODB_URI", default="mongodb://mongo-db:27017")
MONGODB_DB_NAME = config("MONGODB_DB_NAME", default="kidney_stone_detection_db")

# Consul configuration
CONSUL_HOST = config("CONSUL_HOST", default="consul")
CONSUL_PORT = config("CONSUL_PORT", cast=int, default=8500)