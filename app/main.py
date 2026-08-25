from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI

from app.models.schemas import PredictionInput


MODEL_PATH = "ml/saved_model/model.joblib"

model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model

    print("Loading trained model...")
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully.")

    yield

    print("Application shutting down...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "ML API is alive"}


@app.post("/predict")
def predict(house_data: PredictionInput):

    input_data = pd.DataFrame([house_data.model_dump()])

    prediction = model.predict(input_data)

    return {
        "prediction": float(prediction[0])
    }