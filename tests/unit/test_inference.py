import pytest
from app.inference import predict
from fastai.learner import load_learner

import os
import pytest
from fastai.learner import load_learner

@pytest.fixture
def dummy_model():
    # Use the absolute path for the model file
    model_path = os.path.join(os.path.dirname(__file__), "../../model/kidney_model.pkl")
    return load_learner(model_path)

def test_predict_success(dummy_model):
    test_image_path = os.path.join(os.path.dirname(__file__), "../img/Kidney_stone_test.png")
    with open(test_image_path, "rb") as f:
        image_bytes = f.read()
    prediction = dummy_model.predict(image_bytes)
    assert prediction is not None


def test_predict_invalid_image(dummy_model):
    with pytest.raises(ValueError):
        predict(dummy_model, b"not_an_image")
