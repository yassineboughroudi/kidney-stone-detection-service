from fastapi import FastAPI, UploadFile, File, HTTPException
from app.model_loader import load_model
from app.inference import predict
from app.rabbitmq_publisher import publish_event
import logging
from app.config import SERVICE_NAME

app = FastAPI(title="Kidney Stone Detection Microservice")
model = load_model("model/kidney_model.pkl")
logging.basicConfig(level=logging.INFO)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/predict")
async def predict_kidney_stone(file: UploadFile = File(...)):
    try:
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are supported.")
        image = file.file.read()
        prediction_result = predict(model, image)
        publish_event({"service": SERVICE_NAME, "prediction": prediction_result})
        return prediction_result
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
