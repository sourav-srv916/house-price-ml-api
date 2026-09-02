# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

import time
import pandas as pd

from fastapi import APIRouter, HTTPException, Request

from app.logging_config import logger
from app.models.schemas import PredictionInput, PredictionOutput, PredictionBatchInput, PredictionBatchOutput, ModelInfoOutput
from app.exceptions import PredictionInputError
from app.config import settings

# ---------------------------------------------------------
# API VERSION 1 ROUTER
# ---------------------------------------------------------

router = APIRouter(prefix="/api/v1", tags=["Version 1 API"])


# ---------------------------------------------------------
# HEALTH CHECK ENDPOINT
# ---------------------------------------------------------

# This endpoint is used to check whether the API is running
# and whether the ML model has been loaded successfully.
# ---------------------------------------------------------

@router.get("/health")
def health(request: Request):

    request_id = request.state.request_id

    logger.info(
        "Health check called",
        extra={"request_id": request_id}
    )

    model = getattr(request.app.state, "model", None)

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

@router.post("/predict", response_model=PredictionOutput)
def predict(house_data: PredictionInput, request: Request):

    request_id = request.state.request_id

    model = request.app.state.model

    model_info = request.app.state.model_info
    model_version = model_info["model_version"]

    # Convert validated input(Pydantic object) into Python dictionary
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

        logger.error(
            f"Prediction failed: {error}",
            extra={"request_id": request_id}
        )

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

    # Log successful prediction
    logger.info(
        f"Prediction successful: prediction={float(prediction[0])}",
        extra={"request_id": request_id}
    )

    # Return final response
    return {
        "prediction": float(prediction[0]),
        "confidence": confidence,
        "model_version": model_version, 
        "request_id": request_id
    }

# ---------------------------------------------------------
# PREDICTION_BATCH ENDPOINT
# ---------------------------------------------------------

@router.post("/predict-batch", response_model=PredictionBatchOutput)
def predict_batch(batch_data: PredictionBatchInput, request: Request):

    # Get the request ID created by the middleware
    request_id = request.state.request_id

    # Get the model loaded during application startup
    model = request.app.state.model

    model_version = request.app.state.model_info["model_version"]

    # Get the list of houses
    houses = batch_data.houses

    # Number of houses in this batch
    batch_size = len(houses)

    # Enforce configured batch-size limit
    if batch_size > settings.MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum batch size is {settings.MAX_BATCH_SIZE}"
        )


    # Start measuring prediction time
    start_time = time.perf_counter()

    try:
        # Convert every Pydantic object into a dictionary
        house_dicts = [
            house.model_dump()
            for house in houses
        ]

        # Convert all houses into ONE DataFrame
        input_data = pd.DataFrame(house_dicts)

        # Run prediction ONCE for the entire batch
        predictions = model.predict(input_data)

    except Exception as error:

        # Calculate duration even when prediction fails
        duration = time.perf_counter() - start_time

        # Log the actual error internally
        logger.error(
            f"Batch prediction failed: "
            f"batch_size={batch_size}, "
            f"duration={duration:.4f}s, "
            f"error={error}",
            extra={"request_id": request_id}
        )

        # Send a safe error message to the client
        raise HTTPException(
            status_code=500,
            detail="Batch prediction failed"
        )

    # Calculate successful prediction duration
    duration = time.perf_counter() - start_time

    # Convert model predictions into API response objects
    results = []

    for prediction in predictions:
        results.append(
            PredictionOutput(
                prediction=float(prediction),
                confidence=None,
                model_version=model_version, 
                request_id=request_id
            )
        )

    # Log successful batch prediction
    logger.info(
        f"Batch prediction successful: "
        f"batch_size={batch_size}, "
        f"duration={duration:.4f}s",
        extra={"request_id": request_id}
    )

    return {
        "predictions": results
    }

# ---------------------------------------------------------
# MODEL_INFO ENDPOINT
# ---------------------------------------------------------

@router.get("/model-info", response_model=ModelInfoOutput)
def model_info(request: Request):

    request_id = request.state.request_id

    # Get loaded model
    model = request.app.state.model

    # Check whether model is loaded
    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Model is not loaded"
        )

    # Get metadata loaded at startup
    metadata = request.app.state.model_info

    logger.info(
        "Model information requested",
        extra={"request_id": request_id}
    )

    return metadata

# ---------------------------------------------------------
# CHALLENGE — API V2 PLAN
# ---------------------------------------------------------

# If we create /api/v2/predict in the future, we should
# create a separate v2 router and response schema.
#
# Example:
#
# /api/v1/predict
#     -> Existing response contract
#
# /api/v2/predict
#     -> New response contract with additional fields
#
# This allows existing v1 clients to continue working
# without breaking their existing integration.