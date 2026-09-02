# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

from contextlib import asynccontextmanager
import time
import uuid
import json

import joblib

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.logging_config import logger
from app.routers.v1 import router as v1_router
from app.exceptions import PredictionInputError


# ---------------------------------------------------------
# CONFIGURATION settings import from app/config.py
# ---------------------------------------------------------

from app.config import settings

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

    logger.info(
        "Loading trained model...",
        extra={"request_id": "startup"}
    )

    try:

        # Load the saved ML Pipeline/model
        model = joblib.load(settings.MODEL_PATH)

        # Load model metadata
        with open(settings.MODEL_INFO_PATH, "r", encoding="utf-8") as file:
            app.state.model_info = json.load(file)

        logger.info(
            "Model loaded successfully",
            extra={"request_id": "startup"}
        )

        # Save model inside FastAPI app state
        app.state.model = model

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
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
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
# INCLUDE VERSION 1 ROUTES
# ---------------------------------------------------------

app.include_router(v1_router)