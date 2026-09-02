from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ML model configuration
    MODEL_PATH: str
    MODEL_INFO_PATH: str

    # Application configuration
    API_TITLE: str = "House Price Prediction API"
    API_DESCRIPTION: str = "ML API for predicting house prices"
    API_VERSION: str = "1.0.0"

    # Logging configuration
    LOG_LEVEL: str = "INFO"

    # Maximum records allowed in batch prediction
    MAX_BATCH_SIZE: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
