# app/__init__.py

from .main import app  # Import the FastAPI app instance
from .inference import predict  # Import the predict function
from .patient_validator import get_patient_details  # Import get_patient_details
