from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "NETRIKAN - Agentic AI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False

    LOG_LEVEL: str = "INFO"

    MAPS_API_KEY: Optional[str] = None
    CRIME_DATA_PATH: str = str(ROOT_DIR / "datasets" / "crime_data.csv")
    DB_PATH: str = str(ROOT_DIR / "backend" / "data" / "netrikan.db")
    DEMO_USERNAME: str = "student"
    DEMO_PASSWORD: str = "1234"
    RATE_LIMIT_PER_MINUTE: int = 120
    
    # New settings for agent configuration
    AGENT_TIMEOUT: int = 30
    ENABLE_NOTIFICATIONS: bool = True
    SAFETY_THRESHOLD: float = 0.6

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
