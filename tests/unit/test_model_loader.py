import pytest
from app.model_loader import load_model

def test_load_model_success():
    model = load_model("../../model/kidney_model.pkl")
    assert model is not None

def test_load_model_failure():
    with pytest.raises(RuntimeError):
        load_model("model/non_existent_model.pkl")