import sqlite3

from app.models import FareResult
from app.schemas import MonitorCreate, MonitorUpdate
from app.services import monitor_service


def memory_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    return connection


def test_run_monitor_now_saves_results_and_returns_best_offer() -> None:
    connection = memory_connection()
    monitor = monitor_service.create_monitor(
        MonitorCreate(
            origin="MAO",
            destination="GRU",
            departure_date="2026-07-10",
            max_price=1200,
        ),
        connection,
    )

    def fake_search(_monitor):
        return [
            FareResult(
                id=None,
                monitor_id=monitor.id,
                source="amadeus",
                airline="LA",
                total_price=950,
                currency="BRL",
                stops=1,
                duration="PT4H",
                departure_at="2026-07-10T10:00:00",
                return_at=None,
                raw_json="{}",
            ),
            FareResult(
                id=None,
                monitor_id=monitor.id,
                source="amadeus",
                airline="G3",
                total_price=850,
                currency="BRL",
                stops=0,
                duration="PT3H",
                departure_at="2026-07-10T09:00:00",
                return_at=None,
                raw_json="{}",
            ),
        ]

    loaded_monitor, saved_offers, best_offer = monitor_service.run_monitor_now(
        monitor.id,
        connection,
        fake_search,
    )

    assert loaded_monitor == monitor
    assert len(saved_offers) == 2
    assert best_offer is not None
    assert best_offer.total_price == 850
    assert best_offer.id is not None
    assert len(monitor_service.list_fare_results_for_monitor(monitor.id, connection)) == 2


def test_run_monitor_now_returns_none_for_missing_monitor() -> None:
    monitor, offers, best_offer = monitor_service.run_monitor_now(
        999,
        memory_connection(),
        lambda _monitor: [],
    )

    assert monitor is None
    assert offers == []
    assert best_offer is None


def test_run_monitor_now_does_not_search_inactive_monitor() -> None:
    connection = memory_connection()
    monitor = monitor_service.create_monitor(
        MonitorCreate(
            origin="MAO",
            destination="BEL",
            departure_date="2026-07-10",
            max_price=700,
        ),
        connection,
    )
    monitor_service.update_monitor_status(
        monitor.id,
        MonitorUpdate(status="inactive"),
        connection,
    )

    called = False

    def fake_search(_monitor):
        nonlocal called
        called = True
        return []

    loaded_monitor, offers, best_offer = monitor_service.run_monitor_now(
        monitor.id,
        connection,
        fake_search,
    )

    assert loaded_monitor is not None
    assert loaded_monitor.status == "inactive"
    assert offers == []
    assert best_offer is None
    assert called is False
