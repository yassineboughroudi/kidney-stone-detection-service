from fastai.learner import load_learner

def load_model(model_path: str):
    """
    Load the trained model for kidney stone detection.
    """
    try:
        return load_learner(model_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load the model: {e}")