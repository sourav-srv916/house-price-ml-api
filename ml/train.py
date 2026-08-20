from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "train.csv"
MODEL_PATH = BASE_DIR / "ml" / "saved_model" / "model.joblib"


# Features and target
FEATURES = [
    "OverallQual",
    "GrLivArea",
    "BedroomAbvGr",
    "FullBath",
    "GarageCars",
]

TARGET = "SalePrice"


# Load dataset
print("Loading dataset...")
data = pd.read_csv(DATA_PATH)

print(f"Dataset shape: {data.shape}")


# Select features and target
X = data[FEATURES]
y = data[TARGET]


# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)


# Create preprocessing + model pipeline
model = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        (
            "regressor",
            RandomForestRegressor(
                n_estimators=100,
                random_state=42,
            ),
        ),
    ]
)


# Train the model
print("Training model...")
model.fit(X_train, y_train)


# Make predictions on test data
predictions = model.predict(X_test)


# Evaluate the model
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"Mean Absolute Error: {mae:,.2f}")
print(f"R2 Score: {r2:.4f}")


# Create model directory if it doesn't exist
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)


# Save the complete pipeline
joblib.dump(model, MODEL_PATH)

print(f"Model saved to: {MODEL_PATH}")