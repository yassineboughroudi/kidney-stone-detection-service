# tests/unit/test_predict.py
import io
from PIL import Image
import pytest

# Import the predict function from your module.
# Adjust the import below based on your project structure.
from app import predict

# Create a dummy model that simulates the expected behavior.
class DummyModel:
    def predict(self, image):
        # Return a fixed prediction: a label, a placeholder (unused), and probabilities.
        return ("stone", None, [0.1, 0.9])

    @property
    def dls(self):
        class DLS:
            vocab = ["no stone", "stone"]
        return DLS()

def test_predict_success():
    # Create a dummy image
    image = Image.new("RGB", (100, 100), color="white")
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    dummy_model = DummyModel()
    result = predict(dummy_model, img_bytes)

    assert result["class"] == "stone"
    # Check that both vocabulary keys are present in the probabilities
    assert "no stone" in result["probabilities"]
    assert "stone" in result["probabilities"]

def test_predict_failure(monkeypatch):
    # Monkeypatch Image.open so that it raises an exception (simulating a corrupt file)
    monkeypatch.setattr("app.predict.Image.open", lambda x: (_ for _ in ()).throw(Exception("Invalid image")))
    dummy_model = DummyModel()
    with pytest.raises(ValueError) as exc_info:
        predict(dummy_model, b"not an image")
    assert "Prediction failed" in str(exc_info.value)
