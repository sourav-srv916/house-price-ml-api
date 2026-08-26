from contextlib import asynccontextmanager
import uuid

import joblib
import pandas as pd
from fastapi import FastAPI

from app.models.schemas import PredictionInput


# Path to the saved ML model
MODEL_PATH = "ml/saved_model/model.joblib"

# Model variable
model = None


# Load the model once when FastAPI starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model

    print("Loading trained model...")

    model = joblib.load(MODEL_PATH)

    print("Model loaded successfully.")

    yield

    print("Application shutting down...")


# Create FastAPI application
app = FastAPI(
    title="House Price Prediction API",
    description="ML API for predicting house prices",
    version="1.0.0",
    lifespan=lifespan
)


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "ML API is alive"
    }


# Health check endpoint
@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None
    }


# Prediction endpoint
@app.post("/predict")
def predict(house_data: PredictionInput):

    # Generate a unique request ID
    request_id = str(uuid.uuid4())

    # Convert Pydantic object to dictionary
    house_dict = house_data.model_dump()

    # Convert dictionary to DataFrame
    input_data = pd.DataFrame([house_dict])

    # Make prediction
    prediction = model.predict(input_data)

    # Regression model does not support predict_proba()
    confidence = None

    # Return prediction response
    return {
        "request_id": request_id,
        "prediction": float(prediction[0]),
        "confidence": confidence
    }