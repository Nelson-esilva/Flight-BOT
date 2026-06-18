import sqlite3

from app.models import FareResult
from app.rules import generate_alert_hash
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
            max_price=1200,
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


def test_register_alert_sent_persists_alert_hash() -> None:
    connection = memory_connection()
    monitor = create_monitor(connection)
    fare = monitor_service.save_fare_result(make_fare(monitor.id), connection)
    alert_hash = generate_alert_hash(fare, monitor)

    alert = monitor_service.register_alert_sent(monitor, fare, connection)

    assert alert.id is not None
    assert alert.monitor_id == monitor.id
    assert alert.fare_result_id == fare.id
    assert alert.alert_hash == alert_hash
    assert monitor_service.alert_was_sent(alert_hash, connection) is True


def test_same_offer_does_not_create_second_alert() -> None:
    connection = memory_connection()
    monitor = create_monitor(connection)
    fare = monitor_service.save_fare_result(make_fare(monitor.id), connection)

    first_alert = monitor_service.register_alert_sent(monitor, fare, connection)
    second_alert = monitor_service.register_alert_sent(monitor, fare, connection)

    assert second_alert.id == first_alert.id

    rows = connection.execute("SELECT id FROM alerts_sent").fetchall()
    assert len(rows) == 1


def test_different_offer_can_create_new_alert() -> None:
    connection = memory_connection()
    monitor = create_monitor(connection)
    first_fare = monitor_service.save_fare_result(make_fare(monitor.id), connection)
    second_fare = monitor_service.save_fare_result(
        make_fare(monitor.id, total_price=850),
        connection,
    )

    first_alert = monitor_service.register_alert_sent(monitor, first_fare, connection)
    second_alert = monitor_service.register_alert_sent(monitor, second_fare, connection)

    assert second_alert.id != first_alert.id

    rows = connection.execute("SELECT id FROM alerts_sent").fetchall()
    assert len(rows) == 2


def test_should_send_new_alert_returns_false_after_registration() -> None:
    connection = memory_connection()
    monitor = create_monitor(connection)
    fare = monitor_service.save_fare_result(make_fare(monitor.id), connection)

    assert monitor_service.should_send_new_alert(monitor, fare, connection) is True

    monitor_service.register_alert_sent(monitor, fare, connection)

    assert monitor_service.should_send_new_alert(monitor, fare, connection) is False
