import sqlite3

from app.models import Monitor
from app.schemas import MonitorCreate, MonitorUpdate
from app.scheduler import create_scheduler, run_active_monitors
from app.services import monitor_service


def memory_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    return connection


def test_list_active_monitors_returns_only_active_monitors() -> None:
    connection = memory_connection()
    active_monitor = monitor_service.create_monitor(
        MonitorCreate(
            origin="MAO",
            destination="GRU",
            departure_date="2026-07-10",
            max_price=1200,
        ),
        connection,
    )
    inactive_monitor = monitor_service.create_monitor(
        MonitorCreate(
            origin="MAO",
            destination="BEL",
            departure_date="2026-07-10",
            max_price=900,
        ),
        connection,
    )
    monitor_service.update_monitor_status(
        inactive_monitor.id,
        MonitorUpdate(status="inactive"),
        connection,
    )

    active_monitors = monitor_service.list_active_monitors(connection)

    assert active_monitors == [active_monitor]


def test_run_active_monitors_continues_after_monitor_failure(monkeypatch) -> None:
    monitors = [
        Monitor(
            id=1,
            origin="MAO",
            destination="GRU",
            departure_date="2026-07-10",
            return_date=None,
            trip_type="one_way",
            max_price=1200,
            currency="BRL",
            adults=1,
            max_stops=None,
            status="active",
        ),
        Monitor(
            id=2,
            origin="MAO",
            destination="BEL",
            departure_date="2026-07-10",
            return_date=None,
            trip_type="one_way",
            max_price=900,
            currency="BRL",
            adults=1,
            max_stops=None,
            status="active",
        ),
    ]
    monkeypatch.setattr(monitor_service, "list_active_monitors", lambda: monitors)
    called = []

    def runner(monitor_id):
        called.append(monitor_id)
        if monitor_id == 1:
            raise RuntimeError("single monitor failure")

    processed = run_active_monitors(runner)

    assert called == [1, 2]
    assert processed == 1


def test_create_scheduler_uses_configured_interval() -> None:
    scheduler = create_scheduler(lambda _monitor_id: None)
    job = scheduler.get_job("flight_monitor_periodic_check")

    assert job is not None
    assert job.trigger.interval.total_seconds() == 6 * 60 * 60
