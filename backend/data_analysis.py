import pandas as pd

df = pd.read_csv("data/ev_data.csv")
print("\nMISSING VALUES:")
print(df.isnull().sum())
print("DATA")
print(df)

print("\nINFO:")
print(df.info())

print("\nSTATISSTICS:")
print(df.describe())
print("\nINVALID BATTERY VALUES:")
print(df[(df["battery_percentage"] < 0) | (df["battery_percentage"] > 100)])

print("\nINVALID MILEAGE VALUES:")
print(df[df["mileage"] < 0])

#risk-analysis code
def check_risk(row):
    if row["battery_percentage"] < 60 or row["battery_temperature"] > 42:
        return "HIGH"
    elif row["battery_percentage"] < 75 or row["battery_temperature"] > 40:
        return "MEDIUM"
    else:
        return "LOW"


df["risk_level"] = df.apply(check_risk, axis=1)

print("\nEV RISK ANALYSIS:")
print(df[["vehicle_id", "battery_percentage",
          "battery_temperature", "risk_level"]])
high_risk = df[df["risk_level"] == "HIGH"]

print("\nHIGH RISK VEHICLES:")
print(high_risk)

df["health_score"] = (
    df["battery_percentage"] * 0.7
    + (100 - df["battery_temperature"]) * 0.3
)

print("\nBATTERY HEALTH SCORE:")
print(df[["vehicle_id", "health_score"]])