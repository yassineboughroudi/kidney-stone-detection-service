import pytest
import io
import json
from unittest.mock import MagicMock
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo import MongoClient
from PIL import Image
from fastapi.testclient import TestClient

# ✅ Step 1: Apply MongoDB Mock Globally Before Importing FastAPI
mock_collection = MagicMock(spec=Collection)
mock_collection.insert_one.return_value = MagicMock(inserted_id="mock_id")  # Prevent real inserts

mock_db = MagicMock(spec=Database)
mock_db.__getitem__.return_value = mock_collection  # Mock DB collections

mock_client = MagicMock(spec=MongoClient)
mock_client.__getitem__.return_value = mock_db

# ✅ Overwrite MongoClient Before Importing FastAPI
MongoClient = lambda *args, **kwargs: mock_client

# ✅ Step 2: Import FastAPI app **after** setting up mocks
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def override_dependencies(monkeypatch):
    # ✅ 1. Ensure MongoDB is Mocked Before FastAPI Starts
    monkeypatch.setattr("pymongo.MongoClient", lambda *args, **kwargs: mock_client)
    monkeypatch.setattr("app.main.MongoClient", lambda *args, **kwargs: mock_client)

    # ✅ 2. Mock Consul Registration (Prevent network calls)
    def mock_register_service_with_consul():
        return
    monkeypatch.setattr("app.main.register_service_with_consul", mock_register_service_with_consul)

    # ✅ 3. Mock External Patient Service
    def dummy_get_patient_details(patient_id: str):
        return {"id": patient_id, "name": "John Doe"}
    monkeypatch.setattr("app.get_patient_details", dummy_get_patient_details)

    # ✅ 4. Mock RabbitMQ Event Publisher
    def dummy_publish_event(event: dict):
        return
    monkeypatch.setattr("app.publish_event", dummy_publish_event)

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_predict_endpoint_valid_image(client, monkeypatch):
    # ✅ Create a dummy image file to upload.
    image = Image.new("RGB", (100, 100), color="red")
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    # ✅ Mock the predict function to avoid dependency on the actual ML model.
    def dummy_predict(model, file_bytes: bytes):
        return {"class": "stone", "probabilities": {"no stone": 0.1, "stone": 0.9}}
    monkeypatch.setattr("app.inference.predict", dummy_predict)

    response = client.post(
        "/predict",
        files={"file": ("test.png", img_byte_arr, "image/png")},
        data={"patient_id": "123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["prediction"]["class"] == "stone"
    assert data["patient_info"] == {"id": "123", "name": "John Doe"}

def test_predict_endpoint_invalid_file(client):
    # ✅ Test that uploading an unsupported file type returns an error.
    response = client.post(
        "/predict",
        files={"file": ("test.txt", io.BytesIO(b"dummy text"), "text/plain")}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Only JPEG and PNG files supported."
