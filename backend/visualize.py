import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/ev_data.csv")

df["health_score"] = (
    df["battery_percentage"] * 0.7
    + (100 - df["battery_temperature"]) * 0.3
)

plt.bar(df["vehicle_id"], df["health_score"])

plt.xlabel("Vehicle")
plt.ylabel("Health Score")
plt.title("EV Battery Health")

plt.show()