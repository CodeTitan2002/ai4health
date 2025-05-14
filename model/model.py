import joblib
import os
import numpy as np
import pandas as pd

# Load model and training data
CURRENT_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(CURRENT_DIR, "rf_model.pkl")
DATA_PATH = "data/train_data.xlsx"

try:
    rf_model = joblib.load(MODEL_PATH)
    train_df = pd.read_excel(DATA_PATH)
    FEATURE_COLUMNS = train_df.drop(columns=["prognosis"]).columns.tolist()
except Exception as e:
    raise ImportError(f"Failed to load model or data: {str(e)}")

def predict_disease(symptom_array):
    """
    Predict disease based on binary symptom array
    Args:
        symptom_array: List of 0s and 1s corresponding to symptoms
    Returns:
        str: Predicted disease
    """
    if not isinstance(symptom_array, (list, np.ndarray)):
        raise ValueError("Input must be a list or numpy array")
    
    if len(symptom_array) != len(FEATURE_COLUMNS):
        raise ValueError(f"Expected {len(FEATURE_COLUMNS)} features, got {len(symptom_array)}")
    
    if not all(x in [0, 1] for x in symptom_array):
        raise ValueError("All values must be 0 or 1")
    
    try:
        input_array = np.array(symptom_array).reshape(1, -1)
        prediction = rf_model.predict(input_array)
        return prediction[0]
    except Exception as e:
        raise Exception(f"Prediction failed: {str(e)}")