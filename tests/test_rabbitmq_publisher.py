import pika
import pytest
import json
from app.rabbitmq_publisher import publish_event

def test_publish_event(monkeypatch):
    class MockChannel:
        def exchange_declare(self, exchange, exchange_type):
            pass
        def basic_publish(self, exchange, routing_key, body):
            assert exchange == "predictions"
            assert json.loads(body)["service"] == "kidney-stone-service"

    class MockConnection:
        def channel(self):
            return MockChannel()
        def close(self):
            pass

    def mock_connection(*args, **kwargs):
        return MockConnection()

    monkeypatch.setattr(pika, "BlockingConnection", mock_connection)
    publish_event({"service": "kidney-stone-service", "prediction": {"class": "Kidney_stone"}})
