vehicles = [
    {
        "id": "EV001",
        "battery_percentage": 85,
        "battery_temperature": 35.5,
        "battery_capacity": 60
    },
    {
        "id": "EV002",
        "battery_percentage": 90,
        "battery_temperature": 40,
        "battery_capacity": 75
    },
    {
        "id": "EV003",
        "battery_percentage": 72,
        "battery_temperature": 38,
        "battery_capacity": 60
    }
]

for vehicle in vehicles:
    vehicle["remaining_capacity"] = (
        vehicle["battery_capacity"] *
        vehicle["battery_percentage"] / 100
    )

print(vehicles)