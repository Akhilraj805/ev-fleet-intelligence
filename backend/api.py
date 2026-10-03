from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
from collections import Counter
import time

from backend.battery_health import calculate_battery_health
from backend.database import (
    get_all_telemetry,
    get_vehicle_ids,
    get_vehicle_telemetry,
    get_admin_user,
    create_admin_user
)

from backend.predictive_maintenance import (
    calculate_maintenance_risk
)

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from backend.auth import (
    verify_password,
    hash_password,
    create_access_token,
    get_current_user
)
from dotenv import load_dotenv
import os


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://ev-fleet-intelligence-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#temporay define an admin

load_dotenv()

# Load ML model package
model_package = joblib.load(
    "models/ev_fault_model_vehicle_split.pkl"
)

model = model_package["model"]
threshold = model_package["threshold"]
features = model_package["features"]

# -----------------------------
# Fleet Risk Cache
# -----------------------------

fleet_risk_cache = None
fleet_risk_cache_time = 0
FLEET_RISK_CACHE_TTL = 30


#Fleet Data Cache


fleet_data_cache = None
fleet_data_cache_time = 0
FLEET_DATA_CACHE_TTL = 30

fleet_analytics_cache = None
fleet_analytics_cache_time = 0
FLEET_ANALYTICS_CACHE_TTL = 30

def get_processed_fleet_data():

    global fleet_data_cache
    global fleet_data_cache_time

    current_time = time.time()

    if (
        fleet_data_cache is not None
        and current_time - fleet_data_cache_time
        < FLEET_DATA_CACHE_TTL
    ):
        return fleet_data_cache

    df = get_all_telemetry()

    if df.empty:
        return df

    df = calculate_battery_health(df)

    fleet_data_cache = df
    fleet_data_cache_time = current_time

    return fleet_data_cache


# -----------------------------
# EV Input Model
# -----------------------------

class EVData(BaseModel):
    vehicle_id: str
    battery_voltage: float
    battery_current: float
    battery_temperature: float
    soc: float
    motor_temperature: float
    vehicle_speed: float
    odometer: float
    charging_cycles: int
    charging_power: float
    ambient_temperature: float

# -----------------------------
# Home
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "EV Fleet Intelligence API is running"
    }


# -----------------------------
# Initial Admin Setup
# -----------------------------

class AdminSetup(BaseModel):
    username: str
    password: str


@app.post("/auth/setup")
def setup_admin(data: AdminSetup):

    existing_admin = get_admin_user()

    if existing_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin account already exists"
        )

    username = data.username.strip()
    password = data.password

    if len(username) < 3:
        raise HTTPException(
            status_code=400,
            detail="Username must be at least 3 characters"
        )

    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )

    password_hash = hash_password(password)

    create_admin_user(
        username,
        password_hash
    )

    return {
        "message": "Admin account created successfully"
    }
#Login ENDPOINT

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    admin = get_admin_user()

    if not admin:
        raise HTTPException(
            status_code=403,
            detail="No admin account configured. Complete initial setup."
        )

    admin_username, admin_password_hash = admin

    if form_data.username != admin_username:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        form_data.password,
        admin_password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        form_data.username
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# -----------------------------
# Fault + Health Prediction
# -----------------------------

@app.post("/predict")
def predict(
    data: EVData,
    current_user: str = Depends(get_current_user)
):

    # -----------------------------
    # Fault prediction
    # -----------------------------

    input_data = pd.DataFrame([
        data.model_dump(
            exclude={"vehicle_id"}
        )
    ])

    fault_probability = model.predict_proba(
        input_data
    )[0][1]

    prediction = (
        fault_probability >= threshold
    )

    if prediction:
        fault_result = "FAULT LIKELY"
    else:
        fault_result = "NORMAL"


    # -----------------------------
    # Battery health
    # -----------------------------

    history_df = get_vehicle_telemetry(data.vehicle_id)


    # Add current telemetry
    current_df = pd.DataFrame([
        data.model_dump()
    ])

    history_df = pd.concat(
        [
            history_df,
            current_df
        ],
        ignore_index=True
    )


    # Calculate battery health
    history_df = calculate_battery_health(
        history_df
    )

    battery_health = history_df[
        "battery_health"
    ].iloc[-1]


    # -----------------------------
    # Maintenance risk
    # -----------------------------

    if (
        battery_health < 50
        or data.battery_temperature > 48
        or data.motor_temperature > 90
        or data.charging_cycles > 1200
    ):
        maintenance_risk = "HIGH"

    elif (
        battery_health < 70
        or data.battery_temperature > 43
        or data.motor_temperature > 80
        or data.charging_cycles > 1000
    ):
        maintenance_risk = "MEDIUM"

    else:
        maintenance_risk = "LOW"


    # -----------------------------
    # Recommendation
    # -----------------------------

    if battery_health < 50:
        recommendation = (
            "Battery inspection recommended"
        )

    elif data.battery_temperature > 48:
        recommendation = (
            "Check battery cooling system"
        )

    elif data.motor_temperature > 90:
        recommendation = (
            "Inspect motor cooling system"
        )

    elif data.charging_cycles > 1200:
        recommendation = (
            "Battery degradation inspection recommended"
        )

    elif battery_health < 70:
        recommendation = (
            "Schedule battery maintenance"
        )

    else:
        recommendation = (
            "No immediate maintenance required"
        )


    return {
        "fault_prediction": fault_result,
        "fault_probability": round(
            fault_probability * 100,
            2
        ),
        "threshold": threshold * 100,
        "battery_health": round(
            float(battery_health),
            2
        ),
        "maintenance_risk": maintenance_risk,
        "recommendation": recommendation
    }

# -----------------------------
# Get Vehicles
# -----------------------------

@app.get("/vehicles")
def get_vehicles(
    current_user: str = Depends(get_current_user)
):

    vehicles = get_vehicle_ids()

    return {
        "total_vehicles": len(vehicles),
        "vehicles": vehicles["vehicle_id"].tolist()
    }
# -----------------------------
# Get Vehicle Telemetry
# -----------------------------

@app.get("/vehicles/{vehicle_id}")
def get_vehicle(
    vehicle_id: str,
    current_user: str = Depends(get_current_user)
):

    df = get_vehicle_telemetry(vehicle_id)

    if df.empty:
        return {
            "error": "Vehicle not found"
        }

    # Calculate battery health using the centralized function
    df = calculate_battery_health(df)

    # Get latest record
    latest = df.iloc[-1]

    return {
        "vehicle_id": str(latest["vehicle_id"]),
        "timestamp": str(latest["timestamp"]),
        "battery_voltage": float(latest["battery_voltage"]),
        "battery_current": float(latest["battery_current"]),
        "battery_temperature": float(latest["battery_temperature"]),
        "soc": float(latest["soc"]),
        "motor_temperature": float(latest["motor_temperature"]),
        "vehicle_speed": float(latest["vehicle_speed"]),
        "odometer": float(latest["odometer"]),
        "charging_cycles": int(latest["charging_cycles"]),
        "charging_power": float(latest["charging_power"]),
        "ambient_temperature": float(latest["ambient_temperature"]),
        "fault_code": str(latest["fault_code"]),
        "battery_health": round(
            float(latest["battery_health"]),
            2
        )
    }

@app.get("/fleet/summary")
def fleet_summary(
    current_user: str = Depends(get_current_user)
    ):

    df = get_processed_fleet_data()

    if df.empty:
        return {
            "error": "No telemetry data available"
        }

    return {
        "total_vehicles": int(df["vehicle_id"].nunique()),
        "fault_records": int(
            (df["fault_code"] == "FAULT").sum()
        ),
        "normal_records": int(
            (df["fault_code"] == "NORMAL").sum()
        ),
        "average_battery_health": round(
            float(df["battery_health"].mean()),
            2
        ),
        "high_risk_records": int(
            (
                (df["battery_health"] < 50)
                | (df["battery_temperature"] > 48)
                | (df["motor_temperature"] > 90)
                | (df["charging_cycles"] > 1200)
            ).sum()
        )
    }

def calculate_fleet_recent_anomalies(df):

    if df.empty:
        return {}

    df = df.sort_values(
        ["vehicle_id", "timestamp"]
    ).copy()

    # Vehicle-specific normal ranges

    battery_temp_mean = (
        df.groupby("vehicle_id")["battery_temperature"]
        .transform("mean")
    )

    battery_temp_std = (
        df.groupby("vehicle_id")["battery_temperature"]
        .transform("std")
    )

    motor_temp_mean = (
        df.groupby("vehicle_id")["motor_temperature"]
        .transform("mean")
    )

    motor_temp_std = (
        df.groupby("vehicle_id")["motor_temperature"]
        .transform("std")
    )

    voltage_mean = (
        df.groupby("vehicle_id")["battery_voltage"]
        .transform("mean")
    )

    voltage_std = (
        df.groupby("vehicle_id")["battery_voltage"]
        .transform("std")
    )

    # Engineering threshold anomalies

    anomaly_mask = (
        (df["battery_temperature"] > 48)
        |
        (df["motor_temperature"] > 90)
        |
        (df["battery_voltage"] < 350)
        |
        (df["battery_voltage"] > 410)
        |
        (
            (
                abs(
                    df["battery_temperature"]
                    - battery_temp_mean
                )
                > 2 * battery_temp_std
            )
            &
            (df["battery_temperature"] > 45)
        )
        |
        (
            (
                abs(
                    df["motor_temperature"]
                    - motor_temp_mean
                )
                > 2 * motor_temp_std
            )
            &
            (df["motor_temperature"] > 80)
        )
        |
        (
            abs(
                df["battery_voltage"]
                - voltage_mean
            )
            > 2 * voltage_std
        )
    )

    # Last 20 records of each vehicle

    recent_df = (
        df.groupby("vehicle_id")
        .tail(20)
    )

    recent_anomaly_mask = anomaly_mask.loc[
        recent_df.index
    ]

    recent_counts = (
        recent_anomaly_mask
        .groupby(recent_df["vehicle_id"])
        .sum()
        .astype(int)
    )

    return recent_counts.to_dict()

@app.get("/fleet/risk")
def fleet_risk(
    current_user: str = Depends(get_current_user)
):

    global fleet_risk_cache
    global fleet_risk_cache_time

    # -----------------------------
    # Check Cache
    # -----------------------------

    current_time = time.time()

    if (
        fleet_risk_cache is not None
        and current_time - fleet_risk_cache_time
        < FLEET_RISK_CACHE_TTL
    ):
        return fleet_risk_cache

    # -----------------------------
    # Database Loading
    # -----------------------------

    df = get_processed_fleet_data()

    if df.empty:
        return {
            "error": "No telemetry data available"
        }

    fleet_recent_anomalies = calculate_fleet_recent_anomalies(df)

    latest_rows = (
    df.sort_values("timestamp")
    .groupby("vehicle_id")
    .tail(1)
    .copy()
)

    ml_input = latest_rows[features]

    latest_rows["fault_probability"] = model.predict_proba(
            ml_input
        )[:, 1]

    results = []

    # -----------------------------
    # Vehicle Processing
    # -----------------------------

    for vehicle_id, vehicle_df in df.groupby("vehicle_id"):

        vehicle_df = vehicle_df.sort_values(
            "timestamp"
        )

        row = vehicle_df.iloc[-1]

        # -----------------------------
        # AI Fault Probability
        # -----------------------------

        fault_probability = latest_rows.loc[
                latest_rows["vehicle_id"] == vehicle_id,
                "fault_probability"
            ].iloc[0]

        # -----------------------------
        # Recent Anomaly Activity
        # -----------------------------

        recent_anomaly_count = fleet_recent_anomalies.get(
            vehicle_id,
            0
        )
        
        # -----------------------------
        # Maintenance Engine
        # -----------------------------

        maintenance_result = calculate_maintenance_risk(
            battery_health=float(
                row["battery_health"]
            ),
            battery_temperature=float(
                row["battery_temperature"]
            ),
            motor_temperature=float(
                row["motor_temperature"]
            ),
            charging_cycles=float(
                row["charging_cycles"]
            ),
            fault_probability=float(
                fault_probability
            ),
            anomaly_count=recent_anomaly_count
        )

        results.append({
            "vehicle_id": str(vehicle_id),
            "risk": maintenance_result["risk"],
            "maintenance_score":
                maintenance_result["maintenance_score"],
            "battery_health": round(
                float(row["battery_health"]),
                2
            ),
            "battery_temperature": round(
                float(row["battery_temperature"]),
                2
            ),
            "motor_temperature": round(
                float(row["motor_temperature"]),
                2
            ),
            "charging_cycles": int(
                row["charging_cycles"]
            ),
            "fault_probability": round(
                float(fault_probability) * 100,
                2
            ),
            "anomaly_count":
                recent_anomaly_count,
            "recommendation":
                maintenance_result["recommendation"],
            "reasons":
                maintenance_result["reasons"]
        })

    # -----------------------------
    # Risk Counts
    # -----------------------------

    high = sum(
        1 for vehicle in results
        if vehicle["risk"] == "HIGH"
    )

    medium = sum(
        1 for vehicle in results
        if vehicle["risk"] == "MEDIUM"
    )

    low = sum(
        1 for vehicle in results
        if vehicle["risk"] == "LOW"
    )

    # -----------------------------
    # Vehicles Requiring Attention
    # -----------------------------

    attention = [
        vehicle
        for vehicle in results
        if vehicle["risk"] in ["HIGH", "MEDIUM"]
    ]

    attention.sort(
        key=lambda x: x["maintenance_score"],
        reverse=True
    )

    fleet_risk_cache = {
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low,
        "vehicles_requiring_attention": attention
    }

    fleet_risk_cache_time = time.time()

    return fleet_risk_cache

@app.get("/fleet/analytics")
def fleet_analytics(
    current_user: str = Depends(get_current_user)
):

    global fleet_analytics_cache
    global fleet_analytics_cache_time

    current_time = time.time()

    if (
        fleet_analytics_cache is not None
        and current_time - fleet_analytics_cache_time
        < FLEET_ANALYTICS_CACHE_TTL
    ):
        return fleet_analytics_cache

    df = get_processed_fleet_data()

    if df.empty:
        return {
            "error": "No telemetry data available"
        }

    # -----------------------------
    # Latest record for each vehicle
    # -----------------------------

    latest = (
        df.sort_values("timestamp")
        .groupby("vehicle_id")
        .tail(1)
        .copy()
    )

    # -----------------------------
    # Fault distribution
    # -----------------------------

    fault_counts = (
        latest["fault_code"]
        .value_counts()
        .to_dict()
    )

    # -----------------------------
    # Battery health distribution
    # -----------------------------

    health_distribution = {

        "Excellent (80-100)": int(
            (
                latest["battery_health"] >= 80
            ).sum()
        ),

        "Good (60-79)": int(
            (
                (latest["battery_health"] >= 60)
                & (latest["battery_health"] < 80)
            ).sum()
        ),

        "Fair (40-59)": int(
            (
                (latest["battery_health"] >= 40)
                & (latest["battery_health"] < 60)
            ).sum()
        ),

        "Poor (0-39)": int(
            (
                latest["battery_health"] < 40
            ).sum()
        )
    }

    # -----------------------------
    # Temperature statistics
    # -----------------------------

    temperature = {

        "average_battery_temperature": round(
            float(
                latest["battery_temperature"].mean()
            ),
            2
        ),

        "maximum_battery_temperature": round(
            float(
                latest["battery_temperature"].max()
            ),
            2
        ),

        "average_motor_temperature": round(
            float(
                latest["motor_temperature"].mean()
            ),
            2
        ),

        "maximum_motor_temperature": round(
            float(
                latest["motor_temperature"].max()
            ),
            2
        )
    }

    # -----------------------------
    # Charging statistics
    # -----------------------------

    charging = {

        "average_charging_cycles": round(
            float(
                latest["charging_cycles"].mean()
            ),
            2
        ),

        "maximum_charging_cycles": int(
            latest["charging_cycles"].max()
        )
    }

    # -----------------------------
    # Vehicle performance
    # -----------------------------

    performance = {

        "average_speed": round(
            float(
                latest["vehicle_speed"].mean()
            ),
            2
        ),

        "maximum_speed": round(
            float(
                latest["vehicle_speed"].max()
            ),
            2
        )
    }

    fleet_analytics_cache = {
        "total_vehicles": int(
            latest["vehicle_id"].nunique()
        ),

        "fault_distribution": fault_counts,

        "battery_health_distribution":
            health_distribution,

        "temperature": temperature,

        "charging": charging,

        "performance": performance
    }

    fleet_analytics_cache_time = time.time()

    return fleet_analytics_cache

@app.get("/vehicles/{vehicle_id}/history")
def vehicle_history(
    vehicle_id: str,
    current_user: str = Depends(get_current_user)
):

    df = get_vehicle_telemetry(vehicle_id)

    if df.empty:
        return {
            "error": "Vehicle not found"
        }

    return {
        "vehicle_id": vehicle_id,
        "records": df.to_dict(orient="records")
    }

def calculate_anomalies(df):

    if df.empty:
        return {
            "anomaly_count": 0,
            "recent_anomaly_count": 0,
            "anomaly_summary": {},
            "anomalies": []
        }

    battery_temp_mean = df["battery_temperature"].mean()
    battery_temp_std = df["battery_temperature"].std()

    motor_temp_mean = df["motor_temperature"].mean()
    motor_temp_std = df["motor_temperature"].std()

    voltage_mean = df["battery_voltage"].mean()
    voltage_std = df["battery_voltage"].std()

    anomalies = []

    for _, row in df.iterrows():

        reasons = []

        if row["battery_temperature"] > 48:
            reasons.append("High battery temperature")

        if row["motor_temperature"] > 90:
            reasons.append("High motor temperature")

        if row["battery_voltage"] < 350:
            reasons.append("Low battery voltage")

        elif row["battery_voltage"] > 410:
            reasons.append("High battery voltage")

        if (
            abs(
                row["battery_temperature"]
                - battery_temp_mean
            )
            > 2 * battery_temp_std
            and row["battery_temperature"] > 45
        ):
            reasons.append(
                "Unusual battery temperature"
            )

        if (
            abs(
                row["motor_temperature"]
                - motor_temp_mean
            )
            > 2 * motor_temp_std
            and row["motor_temperature"] > 80
        ):
            reasons.append(
                "Unusual motor temperature"
            )

        if (
            abs(
                row["battery_voltage"]
                - voltage_mean
            )
            > 2 * voltage_std
        ):
            reasons.append(
                "Unusual battery voltage"
            )

        reasons = list(
            dict.fromkeys(reasons)
        )

        if reasons:

            anomalies.append({
                "timestamp": row["timestamp"],
                "battery_temperature": round(
                    float(row["battery_temperature"]),
                    2
                ),
                "motor_temperature": round(
                    float(row["motor_temperature"]),
                    2
                ),
                "battery_voltage": round(
                    float(row["battery_voltage"]),
                    2
                ),
                "soc": round(
                    float(row["soc"]),
                    2
                ),
                "reasons": reasons
            })

    recent_records = df.tail(20)

    recent_timestamps = set(
        recent_records["timestamp"]
    )

    recent_anomaly_count = len([
        anomaly
        for anomaly in anomalies
        if anomaly["timestamp"]
        in recent_timestamps
    ])

    reason_counter = Counter()

    for anomaly in anomalies:
        for reason in anomaly["reasons"]:
            reason_counter[reason] += 1

    return {
        "anomaly_count": len(anomalies),
        "recent_anomaly_count": recent_anomaly_count,
        "anomaly_summary": dict(reason_counter),
        "anomalies": anomalies
    }

@app.get("/vehicles/{vehicle_id}/anomalies")
def detect_anomalies(
    vehicle_id: str,
    current_user: str = Depends(get_current_user)
):

    df = get_vehicle_telemetry(vehicle_id)

    if df.empty:
        return {
            "error": "Vehicle not found"
        }

    result = calculate_anomalies(df)

    return {
        "vehicle_id": vehicle_id,
        "total_records": len(df),

        "anomaly_count":
            result["anomaly_count"],

        "anomaly_rate": round(
            (
                result["anomaly_count"]
                / len(df)
            ) * 100,
            2
        ),

        "recent_records_analyzed": min(
            20,
            len(df)
        ),

        "recent_anomaly_count":
            result["recent_anomaly_count"],

        "recent_anomaly_rate": round(
            (
                result["recent_anomaly_count"]
                / min(20, len(df))
            ) * 100,
            2
        ),

        "anomaly_summary":
            result["anomaly_summary"],

        "anomalies":
            result["anomalies"]
    }

@app.get("/vehicles/{vehicle_id}/maintenance")
def predictive_maintenance(
    vehicle_id: str,
    current_user: str = Depends(get_current_user)
):

    df = get_vehicle_telemetry(vehicle_id)

    if df.empty:
        return {
            "error": "Vehicle not found"
        }


    # -----------------------------
    # Battery Health
    # -----------------------------

    df = calculate_battery_health(df)

    battery_health = df[
        "battery_health"
    ].iloc[-1]


    # -----------------------------
    # Latest telemetry
    # -----------------------------

    row = df.iloc[-1]


    # -----------------------------
    # AI Fault Probability
    # -----------------------------

    input_data = pd.DataFrame([
        row[features].to_dict()
    ])

    fault_probability = model.predict_proba(
        input_data
    )[0][1]


    # -----------------------------
    # Anomaly Count
    # -----------------------------

    anomaly_result = calculate_anomalies(df)

    recent_anomaly_count = anomaly_result[
        "recent_anomaly_count"
    ]


    # -----------------------------
    # Maintenance Intelligence
    # -----------------------------

    maintenance_result = calculate_maintenance_risk(

        battery_health=float(
            battery_health
        ),

        battery_temperature=float(
            row["battery_temperature"]
        ),

        motor_temperature=float(
            row["motor_temperature"]
        ),

        charging_cycles=float(
            row["charging_cycles"]
        ),

        fault_probability=float(
            fault_probability
        ),

        anomaly_count=recent_anomaly_count
    )


    # -----------------------------
    # Return Result
    # -----------------------------

    return {
        "vehicle_id": vehicle_id,

        "predictive_maintenance_score":
            maintenance_result[
                "maintenance_score"
            ],

        "risk_level":
            maintenance_result[
                "risk"
            ],

        "battery_health": round(
            float(battery_health),
            2
        ),

        "fault_probability": round(
            fault_probability * 100,
            2
        ),

        "anomaly_count":
            recent_anomaly_count,

        "recommendation":
            maintenance_result[
                "recommendation"
            ],

        "reasons":
            maintenance_result[
                "reasons"
            ]
    }

@app.on_event("startup")
def warm_fleet_cache():

    print("Warming fleet intelligence cache...")

    get_processed_fleet_data()
    fleet_risk(current_user="startup")
    fleet_analytics(current_user="startup")

    print("Fleet intelligence cache ready.")