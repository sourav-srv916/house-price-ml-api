from pydantic import BaseModel, Field
from typing import List


# INPUT MODEL - This model defines what data the user is allowed to send to the /predict endpoint.

class PredictionInput(BaseModel):

    # Overall quality of the house. - Value must be between 1 and 10.
    OverallQual: int = Field(
        ...,
        ge=1,
        le=10,
        description="Overall material and finish quality, from 1 to 10"
    )

    # Above-ground living area in square feet. - Must be greater than 0.
    GrLivArea: float = Field(
        ...,
        gt=0,
        description="Above-ground living area in square feet"
    )

    # Number of bedrooms above ground. - Cannot be negative.
    BedroomAbvGr: int = Field(
        ...,
        ge=0,
        description="Number of bedrooms above ground"
    )

    # Number of full bathrooms. - Cannot be negative.
    FullBath: int = Field(
        ...,
        ge=0,
        description="Number of full bathrooms"
    )

    # Garage capacity. - Cannot be negative.
    GarageCars: int = Field(
        ...,
        ge=0,
        description="Garage capacity in cars"
    )


# OUTPUT MODEL - This model defines exactly what /predict should return.

class PredictionOutput(BaseModel):

    # Predicted house price
    prediction: float

    # Our current regression model does not support predict_proba(), so confidence will be None.
    confidence: float | None

    # Version of the ML model being used
    model_version: str

    # Unique ID generated for every request
    request_id: str


# PREDICTION BATCH INPUT - Accept between 1 and 100 house inputs

class PredictionBatchInput(BaseModel):
    
    houses: List[PredictionInput] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of 1 to 100 house inputs"
    )


# PREDICTION BATCH OUTPUT - Return a list of prediction results

class PredictionBatchOutput(BaseModel):
     
    predictions: List[PredictionOutput]


# MODEL INFO OUTPUT - It makes the endpoint more structured and consistent (optional)

class ModelInfoOutput(BaseModel):

    model_type: str
    model_version: str
    training_date: str
    expected_features: List[str]