# tests/integration/test_endpoints.py
import io
import json
import pytest
from PIL import Image
from fastapi.testclient import TestClient

# Import your FastAPI app.
# Adjust the import according to your project structure.
from app.main import app

# A fixture for the test client.
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def dummy_get_patient_details(patient_id: str):
    # Simulate returning patient details
    return {"id": patient_id, "name": "John Doe"}

def dummy_publish_event(event: dict):
    # Dummy function to override the actual RabbitMQ publisher
    pass

@pytest.fixture(autouse=True)
def override_dependencies(monkeypatch):
    # Mock the Consul registration to prevent errors during testing
    def mock_register_service_with_consul():
        return
    monkeypatch.setattr("app.main.register_service_with_consul", mock_register_service_with_consul)

    # Mock the external patient service call
    def dummy_get_patient_details(patient_id: str):
        return {"id": patient_id, "name": "John Doe"}
    monkeypatch.setattr("app.get_patient_details", dummy_get_patient_details)

    # Mock the RabbitMQ event publisher
    def dummy_publish_event(event: dict):
        return
    monkeypatch.setattr("app.publish_event", dummy_publish_event)

    # Mock the MongoDB collection and client
    class MockCollection:
        def insert_one(self, data):
            return {"_id": "mock_id"}

    class MockDBClient:
        def __init__(self, uri):
            pass
        def __getitem__(self, name):
            return MockCollection()

    monkeypatch.setattr("pymongo.MongoClient", MockDBClient)


def test_predict_endpoint_valid_image(client, monkeypatch):
    # Create a dummy image file to upload.
    image = Image.new("RGB", (100, 100), color="red")
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    # Monkeypatch the predict function to avoid dependency on the actual ML model.
    def dummy_predict(model, file_bytes: bytes):
        return {"class": "stone", "probabilities": {"no stone": 0.1, "stone": 0.9}}
    monkeypatch.setattr("app.predict", dummy_predict)

    response = client.post(
        "/predict",
        files={"file": ("test.png", img_byte_arr, "image/png")},
        data={"patient_id": "123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"]["class"] == "stone"
    # Confirm that the patient info was enriched using our dummy.
    assert data["patient_info"] == {"id": "123", "name": "John Doe"}

def test_predict_endpoint_invalid_file(client):
    # Test that uploading an unsupported file type returns an error.
    response = client.post(
        "/predict",
        files={"file": ("test.txt", io.BytesIO(b"dummy text"), "text/plain")}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Only JPEG and PNG files supported."
