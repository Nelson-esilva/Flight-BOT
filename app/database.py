from pathlib import Path
import sqlite3

from app.config import get_settings


def database_path_from_url(database_url: str) -> str:
    if database_url == "sqlite:///:memory:":
        return ":memory:"

    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise ValueError("Only sqlite:/// database URLs are supported in the MVP")

    return database_url.removeprefix(prefix)


def connect(database_url: str | None = None) -> sqlite3.Connection:
    selected_url = database_url or get_settings().database_url
    database_path = database_path_from_url(selected_url)

    if database_path != ":memory:":
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(connection: sqlite3.Connection | None = None) -> None:
    owns_connection = connection is None
    db = connection or connect()

    try:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS monitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                departure_date TEXT NOT NULL,
                return_date TEXT,
                trip_type TEXT NOT NULL CHECK (trip_type IN ('one_way', 'round_trip')),
                max_price REAL NOT NULL CHECK (max_price > 0),
                currency TEXT NOT NULL DEFAULT 'BRL',
                adults INTEGER NOT NULL DEFAULT 1 CHECK (adults > 0),
                max_stops INTEGER CHECK (max_stops IS NULL OR max_stops >= 0),
                status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS fare_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monitor_id INTEGER NOT NULL,
                source TEXT NOT NULL,
                airline TEXT,
                total_price REAL NOT NULL CHECK (total_price >= 0),
                currency TEXT NOT NULL,
                stops INTEGER CHECK (stops IS NULL OR stops >= 0),
                duration TEXT,
                departure_at TEXT,
                return_at TEXT,
                raw_json TEXT,
                found_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (monitor_id) REFERENCES monitors (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS alerts_sent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monitor_id INTEGER NOT NULL,
                fare_result_id INTEGER,
                alert_hash TEXT NOT NULL UNIQUE,
                sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (monitor_id) REFERENCES monitors (id) ON DELETE CASCADE,
                FOREIGN KEY (fare_result_id) REFERENCES fare_results (id) ON DELETE SET NULL
            );
            """
        )
        db.commit()
    finally:
        if owns_connection:
            db.close()
