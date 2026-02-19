from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "NETRIKAN - Agentic AI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    LOG_LEVEL: str = "INFO"

    MAPS_API_KEY: str | None = None
    CRIME_DATA_PATH: str = "datasets/crime_data.csv"

    class Config:
        env_file = ".env"


settings = Settings()




















