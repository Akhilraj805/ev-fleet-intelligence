import sqlite3
from collections import Counter

import pandas as pd


# --------------------------------
# Load telemetry
# --------------------------------

connection = sqlite3.connect(
    "data/ev_fleet.db"
)

query = """
    SELECT
        vehicle_id,
        timestamp,
        battery_temperature,
        motor_temperature,
        battery_voltage,
        battery_current,
        soc,
        fault_code
    FROM telemetry
    ORDER BY vehicle_id, timestamp ASC
"""

df = pd.read_sql_query(
    query,
    connection
)

connection.close()


# --------------------------------
# Fleet counters
# --------------------------------

total_records = len(df)

total_fault_records = (
    df["fault_code"] == "FAULT"
).sum()

total_anomalies = 0

anomalous_fault_records = 0
anomalous_normal_records = 0

reason_counter = Counter()
reason_fault_counter = Counter()
reason_normal_counter = Counter()


# --------------------------------
# Start analysis
# --------------------------------

print("\n==============================")
print("ANOMALY vs FAULT ANALYSIS")
print("==============================")


# --------------------------------
# Analyze each vehicle
# --------------------------------

for vehicle_id, vehicle_df in df.groupby(
    "vehicle_id"
):

    # -----------------------------
    # Calculate normal ranges
    # -----------------------------

    battery_temp_mean = (
        vehicle_df[
            "battery_temperature"
        ].mean()
    )

    battery_temp_std = (
        vehicle_df[
            "battery_temperature"
        ].std()
    )

    motor_temp_mean = (
        vehicle_df[
            "motor_temperature"
        ].mean()
    )

    motor_temp_std = (
        vehicle_df[
            "motor_temperature"
        ].std()
    )

    voltage_mean = (
        vehicle_df[
            "battery_voltage"
        ].mean()
    )

    voltage_std = (
        vehicle_df[
            "battery_voltage"
        ].std()
    )


    # -----------------------------
    # Detect anomalies
    # -----------------------------

    for _, row in vehicle_df.iterrows():

        reasons = []


        # -------------------------
        # Engineering thresholds
        # -------------------------

        if row["battery_temperature"] > 48:

            reasons.append(
                "High battery temperature"
            )


        if row["motor_temperature"] > 90:

            reasons.append(
                "High motor temperature"
            )


        if row["battery_voltage"] < 350:

            reasons.append(
                "Low battery voltage"
            )

        elif row["battery_voltage"] > 410:

            reasons.append(
                "High battery voltage"
            )


        # -------------------------
        # Statistical anomalies
        # -------------------------

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


        # -------------------------
        # Remove duplicate reasons
        # -------------------------

        reasons = list(
            dict.fromkeys(reasons)
        )


        # -------------------------
        # No anomaly
        # -------------------------

        if not reasons:
            continue


        # -------------------------
        # Count anomaly
        # -------------------------

        total_anomalies += 1


        fault_code = row["fault_code"]


        if fault_code == "FAULT":

            anomalous_fault_records += 1

        elif fault_code == "NORMAL":

            anomalous_normal_records += 1


        # -------------------------
        # Count anomaly reasons
        # -------------------------

        for reason in reasons:

            reason_counter[reason] += 1


            if fault_code == "FAULT":

                reason_fault_counter[
                    reason
                ] += 1

            elif fault_code == "NORMAL":

                reason_normal_counter[
                    reason
                ] += 1


# --------------------------------
# Calculate rates
# --------------------------------

if total_records > 0:

    fleet_anomaly_rate = (
        total_anomalies /
        total_records
    ) * 100

else:

    fleet_anomaly_rate = 0


if total_fault_records > 0:

    fault_anomaly_rate = (
        anomalous_fault_records /
        total_fault_records
    ) * 100

else:

    fault_anomaly_rate = 0


# --------------------------------
# Overall results
# --------------------------------

print(
    f"\nTotal telemetry records: "
    f"{total_records}"
)

print(
    f"Total fault records: "
    f"{total_fault_records}"
)

print(
    f"Total anomalous records: "
    f"{total_anomalies}"
)

print(
    f"Fleet anomaly rate: "
    f"{fleet_anomaly_rate:.2f}%"
)


# --------------------------------
# Anomaly / fault relationship
# --------------------------------

print("\n==============================")
print("ANOMALY / FAULT RELATIONSHIP")
print("==============================")


print(
    f"\nAnomalous records that are FAULT: "
    f"{anomalous_fault_records}"
)

print(
    f"Anomalous records that are NORMAL: "
    f"{anomalous_normal_records}"
)

print(
    f"\nFAULT records detected as anomalies: "
    f"{fault_anomaly_rate:.2f}%"
)


# --------------------------------
# Most common anomaly reasons
# --------------------------------

print("\n==============================")
print("MOST COMMON ANOMALY REASONS")
print("==============================")


for reason, count in (
    reason_counter.most_common()
):

    print(
        f"{reason}: {count}"
    )


# --------------------------------
# Reason / fault analysis
# --------------------------------

print("\n==============================")
print("ANOMALY REASON / FAULT ANALYSIS")
print("==============================")


print(
    f"{'Reason':35}"
    f"{'Total':>8}"
    f"{'FAULT':>8}"
    f"{'NORMAL':>9}"
    f"{'Fault %':>10}"
)

print("-" * 70)


for reason, total in (
    reason_counter.most_common()
):

    fault_count = (
        reason_fault_counter[reason]
    )

    normal_count = (
        reason_normal_counter[reason]
    )

    if total > 0:

        fault_percentage = (
            fault_count /
            total
        ) * 100

    else:

        fault_percentage = 0


    print(
        f"{reason:35}"
        f"{total:8}"
        f"{fault_count:8}"
        f"{normal_count:9}"
        f"{fault_percentage:9.2f}%"
    )


print(
    "\nAnomaly vs fault analysis completed."
)