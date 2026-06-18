import sqlite3

from app.models import FareResult
from app.schemas import MonitorCreate
from app.services import monitor_service


def memory_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    return connection


def create_monitor(connection: sqlite3.Connection):
    return monitor_service.create_monitor(
        MonitorCreate(
            origin="MAO",
            destination="GRU",
            departure_date="2026-07-10",
            max_price=1000,
            max_stops=1,
        ),
        connection,
    )


def make_fare(monitor_id: int, **overrides) -> FareResult:
    data = {
        "id": None,
        "monitor_id": monitor_id,
        "source": "amadeus",
        "airline": "LA",
        "total_price": 900,
        "currency": "BRL",
        "stops": 1,
        "duration": "PT4H",
        "departure_at": "2026-07-10T10:00:00",
        "return_at": None,
        "raw_json": "{}",
    }
    data.update(overrides)
    return FareResult(**data)


def test_run_monitor_now_sends_and_registers_valid_alert() -> None:
    connection = memory_connection()
    monitor = create_monitor(connection)
    sent = []

    result = monitor_service.run_monitor_now(
        monitor.id,
        connection,
        lambda _monitor: [make_fare(monitor.id)],
        lambda sent_monitor, sent_fare: sent.append((sent_monitor, sent_fare)),
    )

    assert result.alerts_sent == 1
    assert result.duplicate_alerts == 0
    assert result.alert_error is None
    assert len(sent) == 1
    assert len(connection.execute("SELECT id FROM alerts_sent").fetchall()) == 1


def test_run_monitor_now_does_not_send_duplicate_alert() -> None:
    connection = memory_connection()
    monitor = create_monitor(connection)
    sent = []

    first_result = monitor_service.run_monitor_now(
        monitor.id,
        connection,
        lambda _monitor: [make_fare(monitor.id)],
        lambda sent_monitor, sent_fare: sent.append((sent_monitor, sent_fare)),
    )
    second_result = monitor_service.run_monitor_now(
        monitor.id,
        connection,
        lambda _monitor: [make_fare(monitor.id)],
        lambda sent_monitor, sent_fare: sent.append((sent_monitor, sent_fare)),
    )

    assert first_result.alerts_sent == 1
    assert second_result.alerts_sent == 0
    assert second_result.duplicate_alerts == 1
    assert len(sent) == 1
    assert len(connection.execute("SELECT id FROM alerts_sent").fetchall()) == 1


def test_run_monitor_now_does_not_send_when_rule_fails() -> None:
    connection = memory_connection()
    monitor = create_monitor(connection)
    sent = []

    result = monitor_service.run_monitor_now(
        monitor.id,
        connection,
        lambda _monitor: [make_fare(monitor.id, total_price=1500)],
        lambda sent_monitor, sent_fare: sent.append((sent_monitor, sent_fare)),
    )

    assert result.alerts_sent == 0
    assert result.duplicate_alerts == 0
    assert sent == []
    assert len(connection.execute("SELECT id FROM fare_results").fetchall()) == 1
    assert len(connection.execute("SELECT id FROM alerts_sent").fetchall()) == 0


def test_telegram_error_does_not_delete_saved_result() -> None:
    connection = memory_connection()
    monitor = create_monitor(connection)

    def failing_sender(_monitor, _fare):
        raise RuntimeError("telegram failed")

    result = monitor_service.run_monitor_now(
        monitor.id,
        connection,
        lambda _monitor: [make_fare(monitor.id)],
        failing_sender,
    )

    assert result.alerts_sent == 0
    assert result.alert_error == "telegram failed"
    assert len(connection.execute("SELECT id FROM fare_results").fetchall()) == 1
    assert len(connection.execute("SELECT id FROM alerts_sent").fetchall()) == 0
