from PIL import Image
from io import BytesIO

def predict(model, file_bytes: bytes):
    """
    Predict the class and probabilities for the given image.
    """
    try:
        image = Image.open(BytesIO(file_bytes)).convert("RGB")
        prediction, _, probabilities = model.predict(image)
        return {
            "class": prediction,
            "probabilities": dict(zip(model.dls.vocab, map(float, probabilities)))
        }
    except Exception as e:
        raise ValueError(f"Prediction failed: {e}")
