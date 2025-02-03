from fastapi import FastAPI, UploadFile, File, HTTPException
from app.model_loader import load_model
from app.inference import predict
from app.rabbitmq_publisher import publish_event
from app.config import SERVICE_NAME, MONGODB_URI, MONGODB_DB_NAME, CONSUL_HOST, CONSUL_PORT
from pymongo import MongoClient
import time
import logging
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Kidney Stone Detection Microservice",
    description="Detect kidney stones from CT scans. Uses MongoDB, RabbitMQ, and Consul.",
    version="1.0.0",
)

logging.basicConfig(level=logging.INFO)

# Load the machine learning model
model = load_model("model/kidney_model.pkl")

# Initialize MongoDB connection
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB_NAME]
predictions_collection = db["predictions"]

CONSUL_SERVICE_ID = SERVICE_NAME

def register_service_with_consul():
    import requests  # Ensure requests is imported
    url = f"http://{CONSUL_HOST}:{CONSUL_PORT}/v1/agent/service/register"
    payload = {
        "ID": CONSUL_SERVICE_ID,
        "Name": SERVICE_NAME,
        "Address": SERVICE_NAME,
        "Port": 8000,
        "Check": {
            "HTTP": f"http://{SERVICE_NAME}:8000/health",
            "Interval": "10s",
            "Timeout": "5s"
        }
    }
    try:
        response = requests.put(url, json=payload)
        if response.status_code == 200:
            logging.info(f"Registered {SERVICE_NAME} with Consul.")
        else:
            logging.error(f"Failed to register service: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Consul registration error: {e}")

@app.on_event("startup")
async def startup_event():
    time.sleep(2)  # Wait for Consul
    register_service_with_consul()
    logging.info(f"{SERVICE_NAME} starting...")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import our helper function
from app.patient_validator import get_patient_details  # Adjust the module name/path as needed

class PredictionResponse(BaseModel):
    patient_id: Optional[str]
    service: str
    prediction: dict
    _id: str
    patient_info: Optional[dict]  # For enrichment

@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_kidney_stone(file: UploadFile = File(...), patient_id: Optional[str] = None):
    """
    Process CT scan for kidney stone detection.
    If patient_id is provided, validate and enrich with patient info.
    """
    try:
        # Validate file type
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(status_code=400, detail="Only JPEG and PNG files supported.")

        # Validate the patient if a patient_id is provided
        patient_info = None
        if patient_id:
            patient_info = get_patient_details(patient_id)
            if patient_info is None:
                raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found.")

        # Read image file and perform prediction
        image_bytes = file.file.read()
        prediction_result = predict(model, image_bytes)

        # Save prediction in MongoDB along with the patient_id
        prediction_data = {
            "patient_id": patient_id,
            "service": SERVICE_NAME,
            "prediction": prediction_result,
        }
        result = predictions_collection.insert_one(prediction_data)
        prediction_data["_id"] = str(result.inserted_id)
        logging.info(f"Stored prediction: {prediction_data}")

        # Publish event via RabbitMQ
        publish_event(prediction_data)

        # Return enriched prediction response including any patient info retrieved
        return {
            **prediction_data,
            "patient_info": patient_info,
        }
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
