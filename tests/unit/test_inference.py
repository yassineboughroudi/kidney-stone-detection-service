import pytest
from app.inference import predict
from fastai.learner import load_learner

@pytest.fixture
def dummy_model():
    return load_learner("../model/kidney_model.pkl")

def test_predict_success(dummy_model):
    with open("../img/Kidney_stone_test.png", "rb") as f:
        file_bytes = f.read()
        result = predict(dummy_model, file_bytes)
        assert "class" in result
        assert "probabilities" in result

def test_predict_invalid_image(dummy_model):
    with pytest.raises(ValueError):
        predict(dummy_model, b"not_an_image")
