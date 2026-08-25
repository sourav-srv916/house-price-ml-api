from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    OverallQual: int = Field(
        ...,
        ge=1,
        le=10,
        description="Overall material and finish quality, from 1 to 10"
    )

    GrLivArea: float = Field(
        ...,
        gt=0,
        description="Above-ground living area in square feet"
    )

    BedroomAbvGr: int = Field(
        ...,
        ge=0,
        description="Number of bedrooms above ground"
    )

    FullBath: int = Field(
        ...,
        ge=0,
        description="Number of full bathrooms"
    )

    GarageCars: int = Field(
        ...,
        ge=0,
        description="Garage capacity in cars"
    )