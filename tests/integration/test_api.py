from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_predict_endpoint():
    with open("tests/sample_image.jpg", "rb") as f:
        response = client.post("/predict", files={"file": f})
        assert response.status_code == 200
        assert "class" in response.json()
        assert "probabilities" in response.json()
