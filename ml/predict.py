from pathlib import Path

import joblib
import pandas as pd


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml" / "saved_model" / "model.joblib"


# Load the saved model
model = joblib.load(MODEL_PATH)

print("Saved model loaded successfully.")


# Example house data
house = pd.DataFrame(
    [
        {
            "OverallQual": 7,
            "GrLivArea": 1800,
            "BedroomAbvGr": 3,
            "FullBath": 2,
            "GarageCars": 2,
        }
    ]
)


# Make prediction
prediction = model.predict(house)[0]

print(f"Predicted house price: ${prediction:,.2f}")