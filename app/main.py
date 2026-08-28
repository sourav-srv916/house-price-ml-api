# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

from contextlib import asynccontextmanager
import time
import uuid

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.models.schemas import PredictionInput, PredictionOutput
from app.logging_config import logger


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

    logger.info(
        "Loading trained model...",
        extra={"request_id": "startup"}
    )

    try:

        # Load the saved ML Pipeline/model
        model = joblib.load(MODEL_PATH)

        logger.info(
            "Model loaded successfully",
            extra={"request_id": "startup"}
        )

    except Exception as error:

        logger.error(
            f"Failed to load model: {error}",
            extra={"request_id": "startup"}
        )

        raise

    # Application continues running after yield
    yield

    logger.info(
        "Application shutting down",
        extra={"request_id": "shutdown"}
    )


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
# REQUEST LOGGING MIDDLEWARE
# ---------------------------------------------------------

@app.middleware("http")
async def logging_middleware(request: Request, call_next):

    # Generate a unique ID for this request
    request_id = str(uuid.uuid4())

    # Store request ID so the endpoint can access it
    request.state.request_id = request_id

    # Record start time
    start_time = time.perf_counter()

    try:

        # Send request to the actual endpoint
        response = await call_next(request)

        return response

    finally:

        # Calculate how long the request took
        duration = time.perf_counter() - start_time

        logger.info(
            f"{request.method} {request.url.path} "
            f"status={getattr(locals().get('response'), 'status_code', 'unknown')} "
            f"duration={duration:.4f}s",
            extra={"request_id": request_id}
        )

# ---------------------------------------------------------
# CUSTOM EXCEPTION HANDLER
# ---------------------------------------------------------

# This handler catches our PredictionInputError
# and returns a clean JSON response instead of
# showing a Python traceback to the client.
# ---------------------------------------------------------

@app.exception_handler(PredictionInputError)
async def prediction_input_error_handler(request: Request, exc: PredictionInputError):

    request_id = request.state.request_id

    logger.error(
        f"Prediction input error: {exc}",
        extra={"request_id": request_id}
    )

    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid prediction input",
            "detail": str(exc),
            "request_id": request_id
        }
    )


# ---------------------------------------------------------
# ROOT ENDPOINT
# ---------------------------------------------------------

@app.get("/")
def root(request: Request):

    request_id = request.state.request_id

    logger.info(
        "Root endpoint called",
        extra={"request_id": request_id}
    )

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
def health(request: Request):

    request_id = request.state.request_id

    logger.info(
        "Health check called",
        extra={"request_id": request_id}
    )

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
def predict(house_data: PredictionInput, request: Request):

    request_id = request.state.request_id

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
        logger.error(
            f"Prediction failed: {error}",
            extra={"request_id": request_id}
        )

         # Return safe error to client
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
    # LOG SUCCESSFUL PREDICTION
    # -----------------------------------------------------

    logger.info(
        f"Prediction successful: prediction={float(prediction[0])}",
        extra={"request_id": request_id}
    )

    # -----------------------------------------------------
    # RETURN FINAL RESPONSE
    # -----------------------------------------------------

    return {
        "prediction": float(prediction[0]),
        "confidence": confidence,
        "model_version": MODEL_VERSION,
        "request_id": request_id
    }