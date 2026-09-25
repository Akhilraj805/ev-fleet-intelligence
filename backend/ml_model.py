import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

import joblib


# --------------------------------
# Load dataset
# --------------------------------

df = pd.read_csv("data/ev_telemetry.csv")

print("Dataset loaded successfully!")
print(f"Total records: {len(df)}")
print(f"Total vehicles: {df['vehicle_id'].nunique()}")


# --------------------------------
# Features
# --------------------------------

features = [
    "battery_voltage",
    "battery_current",
    "battery_temperature",
    "soc",
    "motor_temperature",
    "vehicle_speed",
    "odometer",
    "charging_cycles",
    "charging_power",
    "ambient_temperature"
]


X = df[features]

y = (
    df["fault_code"] == "FAULT"
).astype(int)


# --------------------------------
# Vehicle-based split
# --------------------------------

vehicles = sorted(
    df["vehicle_id"].unique()
)

train_vehicles = vehicles[:80]
test_vehicles = vehicles[80:]


print("\nVehicle split:")
print(f"Training vehicles: {len(train_vehicles)}")
print(f"Testing vehicles: {len(test_vehicles)}")

print(
    f"\nTraining range: "
    f"{train_vehicles[0]} → {train_vehicles[-1]}"
)

print(
    f"Testing range: "
    f"{test_vehicles[0]} → {test_vehicles[-1]}"
)


# --------------------------------
# Create train/test datasets
# --------------------------------

train_df = df[
    df["vehicle_id"].isin(train_vehicles)
]

test_df = df[
    df["vehicle_id"].isin(test_vehicles)
]


X_train = train_df[features]
y_train = (
    train_df["fault_code"] == "FAULT"
).astype(int)

X_test = test_df[features]
y_test = (
    test_df["fault_code"] == "FAULT"
).astype(int)


print("\nDataset split:")
print(f"Training records: {len(X_train)}")
print(f"Testing records: {len(X_test)}")


# --------------------------------
# Train model
# --------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)


print("\nTraining Random Forest...")

model.fit(
    X_train,
    y_train
)


print("Training completed!")


# --------------------------------
# Predictions
# --------------------------------

# Get probability of FAULT
y_probability = model.predict_proba(X_test)[:, 1]

# Default threshold
threshold = 0.35

# Convert probabilities into predictions
y_pred = (
    y_probability >= threshold
).astype(int)

# --------------------------------
# Threshold comparison
# --------------------------------

print("\n==============================")
print("THRESHOLD COMPARISON")
print("==============================")

for threshold in [0.50, 0.45, 0.40, 0.35, 0.30, 0.25]:

    predictions = (
        y_probability >= threshold
    ).astype(int)

    print(
        f"\nThreshold: {threshold}"
    )

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "NORMAL",
                "FAULT"
            ]
        )
    )

# --------------------------------
# Model evaluation
# --------------------------------

accuracy = accuracy_score(
    y_test,
    y_pred
)


print("\n==============================")
print("MODEL EVALUATION")
print("==============================")

print(
    f"\nAccuracy: "
    f"{accuracy * 100:.2f}%"
)


print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "NORMAL",
            "FAULT"
        ]
    )
)


print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# --------------------------------
# Save separate evaluation model
# --------------------------------

model_package = {
    "model": model,
    "threshold": 0.35,
    "features": features
}

joblib.dump(
    model_package,
    "models/ev_fault_model_vehicle_split.pkl"
)

print(
    "\nVehicle-split model package saved!"
)

print(
    "models/ev_fault_model_vehicle_split.pkl"
)