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
    with open("../img/Kidney_stone_test.png", "rb") as f:
        file_bytes = f.read()
        result = predict(dummy_model, file_bytes)
        assert "class" in result
        assert "probabilities" in result

def test_predict_invalid_image(dummy_model):
    with pytest.raises(ValueError):
        predict(dummy_model, b"not_an_image")
