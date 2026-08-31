# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

import pandas as pd

from fastapi import APIRouter, HTTPException, Request

from app.logging_config import logger
from app.models.schemas import PredictionInput, PredictionOutput
from app.exceptions import PredictionInputError

# ---------------------------------------------------------
# API VERSION 1 ROUTER
# ---------------------------------------------------------

router = APIRouter(prefix="/api/v1", tags=["Version 1 API"])

MODEL_VERSION = "1.0"


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
        "model_version": MODEL_VERSION,
        "request_id": request_id
    }


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