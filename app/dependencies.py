from fastapi import Header, HTTPException, Depends
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(x_api_key: str | None = Depends(api_key_header)):
    # Check whether the API key is provided
    if x_api_key is None:
        raise HTTPException(
            status_code=401,
            detail="Missing API key"
        )

    # Check whether the API key is correct
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return x_api_key