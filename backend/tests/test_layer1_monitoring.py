import sys
import unittest
from unittest.mock import MagicMock, patch
import os
from pathlib import Path

# Add backend to sys.path
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))

# Mock joblib before importing
sys.modules["joblib"] = MagicMock()
sys.modules["pandas"] = MagicMock()
sys.modules["numpy"] = MagicMock()

import pandas as pd
import numpy as np
from core.layer1_monitoring import XGBoostPredictor, _model_paths

class TestLayer1Monitoring(unittest.TestCase):
    def setUp(self):
        # Clear any existing predictor state by creating a new instance
        # We need to mock the existence of files and joblib loads
        pass

    @patch('core.layer1_monitoring.Path.exists')
    @patch('joblib.load')
    def test_predictor_load_success(self, mock_load, mock_exists):
        # We want exists to return True for all calls in this test
        mock_exists.return_value = True
        
        mock_model = MagicMock()
        mock_scaler = MagicMock()
        mock_cols = ['lat', 'lon']
        
        # Side effect to return different things for different calls
        mock_load.side_effect = [mock_model, mock_scaler, mock_cols]
        
        predictor = XGBoostPredictor()
        
        self.assertEqual(predictor.model, mock_model)
        self.assertEqual(predictor.scaler, mock_scaler)
        self.assertEqual(predictor.feature_cols, mock_cols)

    @patch('core.layer1_monitoring.Path.exists')
    @patch('joblib.load')
    def test_predictor_load_partial_failure(self, mock_load, mock_exists):
        # We need exists to return True for model and cols, but False for scaler
        # MODEL_PATH is index 0, SCALER_PATH is index 1, FEATURE_COLS_PATH is index 2 in _load_model calls
        # Wait, the order in _load_model is:
        # if MODEL_PATH.exists(): ...
        # if SCALER_PATH.exists(): ...
        # if FEATURE_COLS_PATH.exists(): ...
        
        mock_exists.side_effect = [True, False, True]
        
        mock_model = MagicMock()
        mock_cols = ['lat', 'lon']
        mock_load.side_effect = [mock_model, mock_cols]
        
        predictor = XGBoostPredictor()
        
        self.assertIsNotNone(predictor.model)
        self.assertIsNone(predictor.scaler) # Should be None because exists returned False
        self.assertIsNotNone(predictor.feature_cols)

    def test_predict_fallback_when_none(self):
        # Create a predictor with None components
        predictor = XGBoostPredictor()
        predictor.model = None
        predictor.scaler = None
        
        # Should call _fallback
        res = predictor.predict(0.0, 0.0, 0.0, 12, 'low')
        self.assertEqual(res, 0.2) # Default fallback for low severity at noon

    @patch('pandas.DataFrame')
    def test_predict_success(self, mock_df):
        predictor = XGBoostPredictor()
        predictor.model = MagicMock()
        predictor.scaler = MagicMock()
        predictor.feature_cols = ['a', 'b']
        
        predictor.model.predict.return_value = [0.75]
        predictor.scaler.transform.return_value = np.array([[1, 2]])
        
        res = predictor.predict(12.3, 45.6, 50.0, 10, 'high')
        
        self.assertEqual(res, 0.75)
        predictor.scaler.transform.assert_called_once()
        predictor.model.predict.assert_called_once()

    def test_predict_exception_handling(self):
        predictor = XGBoostPredictor()
        predictor.model = MagicMock()
        predictor.scaler = MagicMock()
        predictor.feature_cols = ['a', 'b']
        
        # Transform raises exception
        predictor.scaler.transform.side_effect = Exception("Transform error")
        
        # Should catch and return fallback
        res = predictor.predict(12.3, 45.6, 50.0, 10, 'high')
        self.assertLessEqual(res, 0.95) # Fallback max is 0.95
        self.assertGreater(res, 0.5) # High severity + morning should be > 0.5

if __name__ == '__main__':
    unittest.main()
