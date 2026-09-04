# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

import pandas as pd

from fastapi import APIRouter, HTTPException, Request

from app.logging_config import logger
from app.models.schemas import PredictionInput, PredictionV2Output


# ---------------------------------------------------------
# API VERSION 2 ROUTER
# ---------------------------------------------------------

router = APIRouter(prefix="/api/v2", tags=["Version 2 API"])


# ---------------------------------------------------------
# PREDICTION V2 ENDPOINT
# ---------------------------------------------------------

@router.post("/predict", response_model=PredictionV2Output)
def predict_v2(house_data: PredictionInput, request: Request):

    # Get request ID from middleware
    request_id = request.state.request_id

    # Get the model loaded during application startup
    model = request.app.state.model

    # Get model version from metadata
    model_info = request.app.state.model_info
    model_version = model_info["model_version"]

    # Convert validated input into a dictionary
    house_dict = house_data.model_dump()

    # Convert input into DataFrame
    input_data = pd.DataFrame([house_dict])

    # Run model prediction
    try:
        prediction = model.predict(input_data)

    except Exception as error:

        logger.error(
            f"V2 prediction failed: {error}",
            extra={"request_id": request_id}
        )

        raise HTTPException(
            status_code=500,
            detail="Prediction failed"
        )

    # Check whether model returned a prediction
    if len(prediction) == 0:

        raise HTTPException(
            status_code=400,
            detail="Model returned an empty prediction"
        )

    # Our regression model does not provide confidence
    confidence = None

    # Log successful prediction
    logger.info(
        f"V2 prediction successful: "
        f"prediction={float(prediction[0])}",
        extra={"request_id": request_id}
    )

    # Return V2 response
    return {
        "prediction": float(prediction[0]),
        "confidence": confidence,
        "model_version": model_version,
        "request_id": request_id,

        # New field introduced in V2
        "prediction_unit": "USD"
    }