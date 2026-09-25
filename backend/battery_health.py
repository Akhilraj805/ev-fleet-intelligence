import pandas as pd


def calculate_battery_health(df):

    # --------------------------------
    # Cycle-based degradation
    # --------------------------------

    cycle_health = (
        100
        - (df["charging_cycles"] / 1500 * 100)
    )

    cycle_health = cycle_health.clip(0, 100)


    # --------------------------------
    # Temperature stress
    # --------------------------------

    temperature_stress = (
        (df["battery_temperature"] - 35) / 20
    ).clip(0, 1)

    temperature_health = (
        100 - temperature_stress * 100
    )


    # --------------------------------
    # Voltage stability
    # --------------------------------

    voltage_deviation = (
        abs(df["battery_voltage"] - 380)
        / 40
    ).clip(0, 1)

    voltage_health = (
        100 - voltage_deviation * 100
    )


    # --------------------------------
    # Raw health estimate
    # --------------------------------

    df["battery_health_raw"] = (
        0.60 * cycle_health
        + 0.25 * temperature_health
        + 0.15 * voltage_health
    )


    # --------------------------------
    # Smooth health for each vehicle
    # --------------------------------

    if "vehicle_id" in df.columns:

        df["battery_health"] = (
            df.groupby("vehicle_id")[
                "battery_health_raw"
            ]
            .transform(
                lambda x:
                x.rolling(
                    window=20,
                    min_periods=1
                ).mean()
            )
        )

    else:

        df["battery_health"] = (
            df["battery_health_raw"]
        )


    # --------------------------------
    # Keep health between 0 and 100
    # --------------------------------

    df["battery_health"] = (
        df["battery_health"]
        .clip(0, 100)
    )


    return df


# --------------------------------
# Test the battery health system
# --------------------------------

if __name__ == "__main__":

    df = pd.read_csv(
        "data/ev_telemetry.csv"
    )

    df = calculate_battery_health(df)

    print("\nBattery Health Statistics")
    print("=========================")

    print(
        df["battery_health"].describe()
    )

    print("\nSample results:")

    print(
        df[
            [
                "vehicle_id",
                "charging_cycles",
                "battery_temperature",
                "battery_voltage",
                "battery_health"
            ]
        ].head(10)
    )

    print("\nHealth trend by vehicle:")

    for vehicle in ["EV001", "EV050", "EV100"]:

        vehicle_data = df[
            df["vehicle_id"] == vehicle
        ]

        first_health = vehicle_data[
            "battery_health"
        ].iloc[0]

        last_health = vehicle_data[
            "battery_health"
        ].iloc[-1]

        first_cycles = vehicle_data[
            "charging_cycles"
        ].iloc[0]

        last_cycles = vehicle_data[
            "charging_cycles"
        ].iloc[-1]

        print(
            f"{vehicle}: "
            f"{first_health:.2f}% → "
            f"{last_health:.2f}% "
            f"({first_cycles} → {last_cycles} cycles)"
        )