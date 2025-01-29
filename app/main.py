import requests
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.model_loader import load_model
from app.inference import predict
from app.rabbitmq_publisher import publish_event
from app.config import SERVICE_NAME, MONGODB_URI, MONGODB_DB_NAME, CONSUL_HOST, CONSUL_PORT
from pymongo import MongoClient
import time

app = FastAPI(title="Kidney Stone Detection Microservice")
logging.basicConfig(level=logging.INFO)

# Load the model
model = load_model("model/kidney_model.pkl")

# Initialize MongoDB connection
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB_NAME]
predictions_collection = db["predictions"]

CONSUL_SERVICE_ID = SERVICE_NAME

def register_service_with_consul():
    """
    Registers the Kidney Stone Detection Service with Consul at startup.
    """
    url = f"http://{CONSUL_HOST}:{CONSUL_PORT}/v1/agent/service/register"

    payload = {
        "ID": CONSUL_SERVICE_ID,
        "Name": SERVICE_NAME,
        "Address": "127.0.0.1",
        "Port": 8000,
        "Check": {
            "HTTP": "http://127.0.0.1:8000/health",
            "Interval": "10s",
            "Timeout": "5s"
        }
    }

    try:
        response = requests.put(url, json=payload)
        if response.status_code == 200:
            logging.info(f"Successfully registered {SERVICE_NAME} with Consul.")
        else:
            logging.error(f"Failed to register service: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to Consul: {e}")

@app.on_event("startup")
async def startup_event():
    """
    Executes on application startup.
    """
    time.sleep(2)  # Delay to ensure Consul is running
    register_service_with_consul()
    logging.info(f"{SERVICE_NAME} is starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Deregisters the service from Consul when the application shuts down.
    """
    url = f"http://{CONSUL_HOST}:{CONSUL_PORT}/v1/agent/service/deregister/{CONSUL_SERVICE_ID}"
    try:
        response = requests.put(url)
        if response.status_code == 200:
            logging.info(f"Successfully deregistered {SERVICE_NAME} from Consul.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error deregistering from Consul: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/predict")
async def predict_kidney_stone(file: UploadFile = File(...), patient_id: str = None):
    """
    Perform prediction, save to MongoDB, and publish the result to RabbitMQ.
    """
    try:
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are supported.")

        # Read and predict the result
        image = file.file.read()
        prediction_result = predict(model, image)

        # Save the result to MongoDB
        prediction_data = {
            "patient_id": patient_id,
            "service": SERVICE_NAME,
            "prediction": prediction_result,
        }
        predictions_collection.insert_one(prediction_data)
        logging.info(f"Saved prediction to MongoDB: {prediction_data}")

        # Publish the result to RabbitMQ
        publish_event(prediction_data)
        return prediction_result
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
