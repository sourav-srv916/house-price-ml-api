# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

from contextlib import asynccontextmanager
import uuid

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import PredictionInput, PredictionOutput


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

# Location of the saved ML model
MODEL_PATH = "ml/saved_model/model.joblib"

# Version of our current ML model
MODEL_VERSION = "1.0"


# ---------------------------------------------------------
# GLOBAL MODEL VARIABLE
# ---------------------------------------------------------

# Initially the model is not loaded.
# It will be loaded when the FastAPI application starts.
model = None


# ---------------------------------------------------------
# CUSTOM EXCEPTION
# ---------------------------------------------------------

# This is our own custom exception.
# We can use it when a specific prediction-related
# problem occurs.
class PredictionInputError(Exception):
    pass


# ---------------------------------------------------------
# APPLICATION LIFESPAN
# ---------------------------------------------------------

# This function runs when the FastAPI application starts.
# The model is loaded ONCE here.
#
# We do NOT load the model inside /predict because that
# would reload the model for every request.
# ---------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    global model

    print("Loading trained model...")

    # Load the saved ML Pipeline/model
    model = joblib.load(MODEL_PATH)

    print("Model loaded successfully.")

    # Application continues running after yield
    yield

    print("Application shutting down...")


# ---------------------------------------------------------
# CREATE FASTAPI APPLICATION
# ---------------------------------------------------------

app = FastAPI(
    title="House Price Prediction API",
    description="ML API for predicting house prices",
    version="1.0.0",
    lifespan=lifespan
)


# ---------------------------------------------------------
# CUSTOM EXCEPTION HANDLER
# ---------------------------------------------------------

# This handler catches our PredictionInputError
# and returns a clean JSON response instead of
# showing a Python traceback to the client.
# ---------------------------------------------------------

@app.exception_handler(PredictionInputError)
async def prediction_input_error_handler(request, exc):

    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid prediction input",
            "detail": str(exc)
        }
    )


# ---------------------------------------------------------
# ROOT ENDPOINT
# ---------------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "ML API is alive"
    }


# ---------------------------------------------------------
# HEALTH CHECK ENDPOINT
# ---------------------------------------------------------

# This endpoint is used to check whether the API is running
# and whether the ML model has been loaded successfully.
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "ok",
        "model_loaded": model is not None
    }


# ---------------------------------------------------------
# PREDICTION ENDPOINT
# ---------------------------------------------------------

# response_model=PredictionOutput tells FastAPI that
# the response must follow the PredictionOutput schema.
# ---------------------------------------------------------

@app.post("/predict", response_model=PredictionOutput)
def predict(house_data: PredictionInput):

    # Generate a unique ID for this request
    request_id = str(uuid.uuid4())

    # Convert Pydantic object into a Python dictionary
    house_dict = house_data.model_dump()


    # -----------------------------------------------------
    # Convert dictionary into a Pandas DataFrame
    #
    # The ML model was trained using a DataFrame with
    # these feature names, so we maintain the same format.
    # -----------------------------------------------------

    input_data = pd.DataFrame([house_dict])


    # -----------------------------------------------------
    # RUN MODEL PREDICTION
    # -----------------------------------------------------

    # model.predict() is the risky operation.
    # If something unexpected happens, the try/except
    # prevents the raw Python error from being exposed
    # to the API user.
    # -----------------------------------------------------

    try:

        prediction = model.predict(input_data)

    except Exception as error:

        # Log the actual error internally.
        # This is useful for developers when debugging.
        print(f"Prediction error: {error}")

        # Send only a safe message to the client.
        raise HTTPException(
            status_code=500,
            detail="Prediction failed"
        )


    # -----------------------------------------------------
    # CHECK WHETHER MODEL RETURNED A PREDICTION
    # -----------------------------------------------------

    # This demonstrates our custom exception handler.
    # Normally model.predict() should return a prediction.
    # -----------------------------------------------------

    if len(prediction) == 0:

        raise PredictionInputError(
            "Model returned an empty prediction"
        )


    # -----------------------------------------------------
    # CONFIDENCE SCORE
    # -----------------------------------------------------

    # Our House Price model is a regression model.
    # Regression models do not normally provide
    # predict_proba(), so confidence is not available.
    # Therefore we return None.
    # -----------------------------------------------------

    confidence = None


    # -----------------------------------------------------
    # RETURN FINAL RESPONSE
    # -----------------------------------------------------

    return {
        "prediction": float(prediction[0]),
        "confidence": confidence,
        "model_version": MODEL_VERSION,
        "request_id": request_id
    }