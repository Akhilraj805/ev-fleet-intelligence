# backend/predictive_maintenance.py

def calculate_maintenance_risk(
    battery_health,
    battery_temperature,
    motor_temperature,
    charging_cycles,
    fault_probability=0.0,
    anomaly_count=0
):

    score = 0
    reasons = []


    # --------------------------------
    # Battery health
    # --------------------------------

    if battery_health < 50:

        score += 30
        reasons.append(
            "Battery health below 50%"
        )

    elif battery_health < 70:

        score += 15
        reasons.append(
            "Battery health below 70%"
        )


    # --------------------------------
    # Battery temperature
    # --------------------------------

    if battery_temperature > 48:

        score += 25
        reasons.append(
            "High battery temperature"
        )

    elif battery_temperature > 43:

        score += 10
        reasons.append(
            "Elevated battery temperature"
        )


    # --------------------------------
    # Motor temperature
    # --------------------------------

    if motor_temperature > 90:

        score += 20
        reasons.append(
            "High motor temperature"
        )

    elif motor_temperature > 80:

        score += 10
        reasons.append(
            "Elevated motor temperature"
        )


    # --------------------------------
    # Charging cycles
    # --------------------------------

    if charging_cycles > 1200:

        score += 20
        reasons.append(
            "High charging cycle count"
        )

    elif charging_cycles > 1000:

        score += 10
        reasons.append(
            "Charging cycle count is high"
        )


    # --------------------------------
    # AI fault probability
    # --------------------------------

    if fault_probability >= 0.70:

        score += 25
        reasons.append(
            "High AI fault probability"
        )

    elif fault_probability >= 0.50:

        score += 15
        reasons.append(
            "Elevated AI fault probability"
        )

    elif fault_probability >= 0.35:

        score += 10
        reasons.append(
            "AI fault probability above threshold"
        )


    # --------------------------------
    # Recent anomaly activity
    # --------------------------------

    if anomaly_count >= 10:

        score += 15
        reasons.append(
            "Multiple recent anomalies detected"
        )

    elif anomaly_count >= 5:

        score += 10
        reasons.append(
            "Several recent anomalies detected"
        )

    elif anomaly_count >= 1:

        score += 5
        reasons.append(
            "Recent anomaly detected"
        )


    # --------------------------------
    # Limit score
    # --------------------------------

    score = min(
        score,
        100
    )


    # --------------------------------
    # Risk level
    # --------------------------------

    if score >= 60:

        risk = "HIGH"

    elif score >= 30:

        risk = "MEDIUM"

    else:

        risk = "LOW"


    # --------------------------------
    # Recommendation
    # --------------------------------

    if risk == "HIGH":

        recommendation = (
            "Immediate vehicle inspection recommended"
        )

    elif risk == "MEDIUM":

        recommendation = (
            "Schedule preventive maintenance"
        )

    else:

        recommendation = (
            "No immediate maintenance required"
        )


    return {
        "maintenance_score": score,
        "risk": risk,
        "recommendation": recommendation,
        "reasons": reasons
    }