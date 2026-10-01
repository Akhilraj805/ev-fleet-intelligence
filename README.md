# EV Fleet Intelligence Platform

An AI-powered EV fleet monitoring and predictive maintenance platform designed to analyze electric vehicle telemetry, estimate battery health, detect abnormal vehicle behavior, predict potential faults, and support maintenance decisions.

## Overview

The EV Fleet Intelligence Platform is a prototype system for monitoring a fleet of electric vehicles through telemetry data.

The platform processes vehicle and battery parameters such as battery voltage, battery current, battery temperature, state of charge, motor temperature, vehicle speed, odometer, charging cycles, charging power, and ambient temperature.

The collected data is processed through a backend system that combines data analysis, machine learning, anomaly detection, battery health estimation, and predictive maintenance logic.

The results are presented through a web-based fleet dashboard.

## Project Objective

The objective of this project is to develop an intelligent EV fleet monitoring platform that can:

- Monitor EV telemetry data
- Estimate battery health
- Detect abnormal vehicle behavior
- Predict potential vehicle faults using machine learning
- Calculate predictive maintenance risk
- Provide maintenance recommendations
- Provide fleet-level analytics
- Allow administrators to monitor individual vehicles

## Key Features

### Fleet Dashboard

Provides an overview of the entire fleet including:

- Total number of vehicles
- Fault records
- Average battery health
- High-risk records
- Fleet fault distribution
- Battery health distribution

### Vehicle Monitoring

Administrators can view individual vehicle information including:

- Battery voltage
- Battery current
- Battery temperature
- Motor temperature
- State of charge
- Vehicle speed
- Odometer
- Charging cycles
- Charging power
- Ambient temperature
- Fault status
- Estimated battery health

### AI Fault Prediction

A Random Forest classification model estimates the probability that a vehicle telemetry record represents a potential fault condition.

The model uses:

- Battery voltage
- Battery current
- Battery temperature
- State of charge
- Motor temperature
- Vehicle speed
- Odometer
- Charging cycles
- Charging power
- Ambient temperature

The prototype uses a decision threshold of `0.35` for fault classification.

### Battery Health Estimation

The platform calculates an estimated battery health indicator using:

- Charging cycle degradation
- Battery temperature stress
- Battery voltage deviation

The calculated health score is smoothed using recent vehicle records.

This is an estimated health indicator for the prototype and should not be interpreted as laboratory-measured battery State of Health (SOH).

### Anomaly Detection

The system detects abnormal telemetry behavior using:

- Engineering thresholds
- Vehicle-specific statistical ranges
- Temperature deviations
- Motor temperature deviations
- Battery voltage deviations

### Predictive Maintenance

The maintenance engine combines:

- Battery health
- Battery temperature
- Motor temperature
- Charging cycles
- AI fault probability
- Recent anomaly activity

The resulting risk level is classified as:

- LOW
- MEDIUM
- HIGH

The system also generates a maintenance recommendation.

### Authentication

The platform includes administrator authentication using:

- JWT access tokens
- Password hashing with Argon2
- Protected FastAPI endpoints
- Frontend authentication handling

## System Architecture

```text
EV Telemetry Data
        |
        v
SQLite Database
        |
        v
FastAPI Backend
        |
        +-------------------+
        |                   |
        v                   v
Data Processing        ML Model
        |                   |
        |             Fault Prediction
        |
        +-------------------+
        |
        +-------------------+
        |                   |
        v                   v
Battery Health       Anomaly Detection
        |                   |
        +---------+---------+
                  |
                  v
       Predictive Maintenance
                  |
                  v
           Fleet Analytics
                  |
                  v
            Web Dashboard
```

## Machine Learning Model

The platform uses a Random Forest Classifier for EV fault prediction.

### Model Configuration

- Algorithm: Random Forest Classifier
- Number of estimators: 200
- Class weighting: Balanced
- Random state: 42
- Decision threshold: 0.35

The prototype uses a vehicle-based train/test split to evaluate the model on vehicles that were not used during training.

### Dataset Split

```text
Training vehicles:
EV001 - EV080

Testing vehicles:
EV081 - EV100
```

### Input Features

- Battery voltage
- Battery current
- Battery temperature
- State of charge
- Motor temperature
- Vehicle speed
- Odometer
- Charging cycles
- Charging power
- Ambient temperature

## Battery Health Estimation

The battery health calculation combines three main indicators:

```text
Charging Cycle Health
        +
Temperature Health
        +
Voltage Health
        |
        v
Estimated Battery Health
```

The prototype uses:

```text
Charging cycle health : 60%
Temperature health    : 25%
Voltage health        : 15%
```

The resulting health value is constrained between `0` and `100`.

A rolling average over recent vehicle records is used to smooth the health indicator.

## Predictive Maintenance Logic

The maintenance engine calculates a maintenance score based on multiple conditions, including:

- Low battery health
- High battery temperature
- High motor temperature
- High charging cycle count
- High AI fault probability
- Recent anomalies

The resulting score is classified as:

```text
0 - 29    -> LOW
30 - 59   -> MEDIUM
60 - 100  -> HIGH
```

## Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Pandas
- NumPy
- Scikit-learn
- Joblib

### Database

- SQLite

### Authentication

- JWT
- PyJWT
- pwdlib
- Argon2

### Frontend

- HTML
- CSS
- JavaScript
- Chart.js

### Development Tools

- Visual Studio Code
- Python Virtual Environment
- Git
- GitHub

## Project Structure

```text
EV-FLEET-INTELLIGENCE/
│
├── backend/
│   ├── api.py
│   ├── auth.py
│   ├── battery_health.py
│   ├── database.py
│   ├── data_analysis.py
│   ├── generate_data.py
│   ├── ml_model.py
│   └── predictive_maintenance.py
│
├── data/
│   ├── ev_data.csv
│   └── ev_telemetry.csv
│
├── frontend/
│   ├── index.html
│   ├── vehicles.html
│   ├── vehicle-details.html
│   ├── analytics.html
│   ├── maintenance.html
│   ├── attention.html
│   ├── login.html
│   ├── script.js
│   └── style.css
│
├── models/
│   ├── ev_fault_model.pkl
│   └── ev_fault_model_vehicle_split.pkl
│
├── .gitignore
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Akhilraj805/ev-fleet-intelligence.git
cd ev-fleet-intelligence
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install the required dependencies:

```bash
pip install fastapi uvicorn pandas numpy scikit-learn joblib pyjwt "pwdlib[argon2]" python-multipart python-dotenv
```

## Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD_HASH=your-password-hash
```

The `.env` file is excluded from Git using `.gitignore`.

## Running the Backend

Start the FastAPI server:

```bash
uvicorn backend.api:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Authentication

```text
POST /auth/login
```

### Fleet

```text
GET /vehicles
GET /fleet/summary
GET /fleet/risk
GET /fleet/analytics
```

### Vehicle

```text
GET /vehicles/{vehicle_id}
GET /vehicles/{vehicle_id}/history
GET /vehicles/{vehicle_id}/anomalies
GET /vehicles/{vehicle_id}/maintenance
```

### AI Prediction

```text
POST /predict
```

Protected endpoints require a valid JWT access token.

## Prototype Dataset

The project currently uses synthetically generated EV telemetry data for development and testing.

The telemetry dataset contains:

- vehicle_id
- timestamp
- battery_voltage
- battery_current
- battery_temperature
- motor_temperature
- vehicle_speed
- odometer
- charging_cycles
- charging_power
- ambient_temperature
- soc
- fault_code

## Limitations

This project is a prototype and has several limitations:

- The telemetry dataset is synthetically generated.
- Battery health is an estimated health indicator rather than laboratory-measured State of Health (SOH).
- The machine learning model has not been validated using a real-world EV fleet dataset.
- Fault prediction performance may change with real-world operational data.
- Predictive maintenance rules are prototype engineering logic.
- The system is not intended to directly control vehicle systems or make safety-critical decisions.

## Future Improvements

Possible future improvements include:

- Integration with real EV telemetry systems
- Real-world fleet datasets
- Improved battery State of Health estimation
- Time-series machine learning models
- Advanced anomaly detection
- Model monitoring and retraining
- Cloud deployment
- Role-based access control
- Real-time telemetry streaming
- Automated maintenance scheduling
- Fleet-level forecasting
- Vehicle diagnostic system integration

## Project Status

The current prototype includes:

- EV telemetry data processing
- SQLite database
- FastAPI backend
- JWT authentication
- Random Forest fault prediction
- Battery health estimation
- Anomaly detection
- Predictive maintenance scoring
- Fleet analytics
- Web dashboard
- Vehicle monitoring
- Light and dark themes

The system is currently intended as a prototype for demonstrating EV fleet intelligence and predictive maintenance concepts.

## Author

Developed as a personal EV fleet intelligence project.
