import pandas as pd
import numpy as np

np.random.seed(42)

# --------------------------------
# Fleet configuration
# --------------------------------

number_of_vehicles = 100
records_per_vehicle = 120

vehicles = [
    f"EV{i:03d}"
    for i in range(1, number_of_vehicles + 1)
]

data = []

# --------------------------------
# Generate telemetry
# --------------------------------

for vehicle in vehicles:

    # Vehicle-specific characteristics

    battery_age = np.random.uniform(0, 1)

    temperature_bias = np.random.normal(0, 2)

    motor_bias = np.random.normal(0, 3)

    voltage_bias = np.random.normal(0, 5)

    cycle_start = np.random.randint(100, 1200)

    for record in range(records_per_vehicle):

        # Gradual degradation
        degradation = (
            battery_age
            + record / records_per_vehicle * 0.15
        )

        battery_temperature = (
            np.random.normal(38, 4)
            + temperature_bias
            + degradation * 8
        )

        motor_temperature = (
            np.random.normal(65, 8)
            + motor_bias
            + degradation * 10
        )

        battery_voltage = (
            np.random.normal(380, 10)
            + voltage_bias
            - degradation * 8
        )

        battery_current = np.random.normal(
            50,
            12
        )

        soc = np.random.uniform(
            20,
            100
        )

        vehicle_speed = np.random.uniform(
            0,
            120
        )

        charging_cycles = (
            cycle_start
            + record
        )

        charging_power = np.random.uniform(
            0,
            100
        )

        ambient_temperature = np.random.normal(
            30,
            6
        )

        odometer = (
            np.random.uniform(10000, 90000)
            + record * np.random.uniform(1, 10)
        )

        # --------------------------------
        # Hidden risk score
        # --------------------------------

        risk_score = 0

        # Temperature contribution

        if battery_temperature > 45:
            risk_score += 2

        if battery_temperature > 50:
            risk_score += 2

        # Motor contribution

        if motor_temperature > 80:
            risk_score += 2

        if motor_temperature > 95:
            risk_score += 2

        # Voltage contribution

        if abs(battery_voltage - 380) > 20:
            risk_score += 2

        # Charging contribution

        if charging_cycles > 1000:
            risk_score += 1

        if charging_cycles > 1300:
            risk_score += 2

        # SOC contribution

        if soc < 30:
            risk_score += 1

        # Add random real-world uncertainty

        risk_score += np.random.normal(
            0,
            1.5
        )

        # --------------------------------
        # Convert risk into probability
        # --------------------------------

        fault_probability = (
            1 /
            (
                1 +
                np.exp(
                    -(risk_score - 5)
                )
            )
        )

        fault = (
            np.random.random()
            < fault_probability
        )

        fault_code = (
            "FAULT"
            if fault
            else "NORMAL"
        )

        data.append({

            "vehicle_id": vehicle,

            "timestamp":
                pd.Timestamp("2026-01-01")
                + pd.Timedelta(
                    minutes=len(data)
                ),

            "battery_voltage":
                battery_voltage,

            "battery_current":
                battery_current,

            "battery_temperature":
                battery_temperature,

            "soc":
                soc,

            "motor_temperature":
                motor_temperature,

            "vehicle_speed":
                vehicle_speed,

            "odometer":
                odometer,

            "charging_cycles":
                charging_cycles,

            "charging_power":
                charging_power,

            "ambient_temperature":
                ambient_temperature,

            "fault_code":
                fault_code
        })


# --------------------------------
# Create DataFrame
# --------------------------------

df = pd.DataFrame(data)

df.to_csv(
    "data/ev_telemetry.csv",
    index=False
)


print(
    "Realistic EV telemetry dataset generated successfully!"
)

print(
    f"\nDataset shape: {df.shape}"
)

print(
    f"\nNumber of vehicles: "
    f"{df['vehicle_id'].nunique()}"
)

print(
    "\nFault distribution:"
)

print(
    df["fault_code"].value_counts()
)

print(
    "\nSample data:"
)

print(
    df.head()
)