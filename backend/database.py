import sqlite3
import pandas as pd
from pathlib import Path


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "ev_fleet.db"
CSV_PATH = BASE_DIR / "data" / "ev_telemetry.csv"


# Create database automatically if it does not exist
def initialize_database():

    if DB_PATH.exists():
        return

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CSV_PATH)

    with sqlite3.connect(DB_PATH) as connection:

        df.to_sql(
            "telemetry",
            connection,
            if_exists="replace",
            index=False
        )

    print("Database created from telemetry CSV.")


# Manual database creation / testing
if __name__ == "__main__":

    connection = sqlite3.connect(DB_PATH)

    df = pd.read_csv(CSV_PATH)

    df.to_sql(
        "telemetry",
        connection,
        if_exists="replace",
        index=False
    )

    print("Database created successfully!")

    print("\nTotal telemetry records:")
    print(len(df))

    query = "SELECT * FROM telemetry LIMIT 5"

    result = pd.read_sql_query(
        query,
        connection
    )

    print("\nFirst 5 records:")
    print(result)

    connection.close()


# Database connection
def get_connection():

    initialize_database()

    return sqlite3.connect(DB_PATH)


# Get all telemetry
def get_all_telemetry():

    connection = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM telemetry",
        connection
    )

    connection.close()

    return df


# Get telemetry for one vehicle
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


# Get all vehicle IDs
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

# -----------------------------
# Admin User Management
# -----------------------------

def initialize_admin_table():

    with get_connection() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
            """
        )

        connection.commit()


def get_admin_user():

    initialize_admin_table()

    with get_connection() as connection:

        return connection.execute(
            """
            SELECT username, password_hash
            FROM admin_users
            LIMIT 1
            """
        ).fetchone()


def create_admin_user(username, password_hash):

    initialize_admin_table()

    with get_connection() as connection:

        connection.execute(
            """
            INSERT INTO admin_users
            (username, password_hash)
            VALUES (?, ?)
            """,
            (username, password_hash)
        )

        connection.commit()