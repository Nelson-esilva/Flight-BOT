import sqlite3

from app.schemas import MonitorCreate, MonitorUpdate
from app.services import monitor_service


def test_create_and_list_monitor() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    monitor = monitor_service.create_monitor(
        MonitorCreate(
            origin="mao",
            destination="gru",
            departure_date="2026-07-10",
            max_price=1200,
        ),
        connection,
    )

    assert monitor.id == 1
    assert monitor.origin == "MAO"
    assert monitor.destination == "GRU"
    assert monitor.currency == "BRL"
    assert monitor.status == "active"
    assert len(monitor_service.list_monitors(connection)) == 1


def test_round_trip_requires_return_date() -> None:
    try:
        MonitorCreate(
            origin="MAO",
            destination="GRU",
            departure_date="2026-07-10",
            trip_type="round_trip",
            max_price=1200,
        )
    except ValueError as exc:
        assert "return_date is required" in str(exc)
    else:
        raise AssertionError("round_trip without return_date should fail")


def test_update_monitor_status() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    monitor = monitor_service.create_monitor(
        MonitorCreate(
            origin="MAO",
            destination="BEL",
            departure_date="2026-07-10",
            max_price=900,
        ),
        connection,
    )

    updated = monitor_service.update_monitor_status(
        monitor.id,
        MonitorUpdate(status="inactive"),
        connection,
    )

    assert updated is not None
    assert updated.status == "inactive"


def test_delete_monitor() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    monitor = monitor_service.create_monitor(
        MonitorCreate(
            origin="MAO",
            destination="REC",
            departure_date="2026-07-10",
            max_price=1000,
        ),
        connection,
    )

    assert monitor_service.delete_monitor(monitor.id, connection) is True
    assert monitor_service.get_monitor(monitor.id, connection) is None
