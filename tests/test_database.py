import sqlite3

from app.database import connect, database_path_from_url, initialize_database


def test_database_path_from_sqlite_url() -> None:
    assert database_path_from_url("sqlite:///data/flight_bot.db") == "data/flight_bot.db"
    assert database_path_from_url("sqlite:///:memory:") == ":memory:"


def test_initialize_database_creates_mvp_tables() -> None:
    connection = sqlite3.connect(":memory:")

    initialize_database(connection)

    table_names = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }

    assert {"monitors", "fare_results", "alerts_sent"}.issubset(table_names)


def test_connect_initializes_sqlite_file_parent(tmp_path) -> None:
    database_file = tmp_path / "nested" / "flight_bot.db"

    connection = connect(f"sqlite:///{database_file}")
    connection.close()

    assert database_file.exists()
