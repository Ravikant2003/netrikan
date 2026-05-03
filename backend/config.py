from pathlib import Path
import os

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(Path(__file__).resolve().parent / ".env")

class Settings:
    APP_NAME: str = "Netrikan"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    ENABLE_NOTIFICATIONS: bool = True
    
    # New settings from project copy
    CRIME_DATA_PATH: str = str(ROOT_DIR / "datasets" / "crime_hotspots.csv")
    SAFETY_THRESHOLD: float = 0.6

settings = Settings()
