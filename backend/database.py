import sqlite3
import pandas as pd

if __name__ == "__main__":


    # Connect to database
    connection = sqlite3.connect("data/ev_fleet.db")


    # Load telemetry CSV
    df = pd.read_csv("data/ev_telemetry.csv")


    # Store telemetry data in SQLite
    df.to_sql(
        "telemetry",
        connection,
        if_exists="replace",
        index=False
    )


    print("Database created successfully!")

    print("\nTotal telemetry records:")
    print(len(df))


    # Check database
    query = "SELECT * FROM telemetry LIMIT 5"

    result = pd.read_sql_query(query, connection)

    print("\nFirst 5 records:")
    print(result)


    # Close connection
    connection.close()

def get_connection():
    return sqlite3.connect(
        "data/ev_fleet.db"
    )


def get_all_telemetry():
    connection = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM telemetry",
        connection
    )

    connection.close()

    return df


def get_vehicle_telemetry(vehicle_id):
    with get_connection() as connection:

        df = pd.read_sql_query(
            """
            SELECT *
            FROM telemetry
            WHERE vehicle_id = ?
            ORDER BY timestamp ASC
            """,
            connection,
            params=(vehicle_id,)
        )

    return df


def get_vehicle_ids():

    with get_connection() as connection:

        vehicles = pd.read_sql_query(
            """
            SELECT DISTINCT vehicle_id
            FROM telemetry
            ORDER BY vehicle_id
            """,
            connection
        )

    return vehicles