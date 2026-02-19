import joblib
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("ModelLoader")


class ModelLoader:
    """
    Safely loads ML models with fallback support.
    """

    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.model = None

    def load(self):
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                logger.info(f"Loaded model from {self.model_path}")
            except Exception as e:
                logger.error(f"Model loading failed: {e}")
                self.model = None
        else:
            logger.warning("Model file not found, using fallback logic")
        return self.model
