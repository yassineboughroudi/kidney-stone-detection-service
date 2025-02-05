import os

import pytest
from app.model_loader import load_model

def test_load_model_success():
    # Use the absolute path for the model file
    model_path = os.path.join(os.path.dirname(__file__), "../../model/kidney_model.pkl")
    model = load_model(model_path)
    assert model is not None

def test_load_model_failure():
    with pytest.raises(RuntimeError):
        load_model("model/non_existent_model.pkl")