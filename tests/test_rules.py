from app.models import FareResult, Monitor
from app.rules import generate_alert_hash, should_alert


def make_monitor(**overrides) -> Monitor:
    data = {
        "id": 1,
        "origin": "MAO",
        "destination": "GRU",
        "departure_date": "2026-07-10",
        "return_date": None,
        "trip_type": "one_way",
        "max_price": 1000.0,
        "currency": "BRL",
        "adults": 1,
        "max_stops": 1,
        "status": "active",
    }
    data.update(overrides)
    return Monitor(**data)


def make_fare(**overrides) -> FareResult:
    data = {
        "id": 1,
        "monitor_id": 1,
        "source": "amadeus",
        "airline": "LA",
        "total_price": 900.0,
        "currency": "BRL",
        "stops": 1,
        "duration": "PT4H",
        "departure_at": "2026-07-10T10:00:00",
        "return_at": None,
        "raw_json": None,
    }
    data.update(overrides)
    return FareResult(**data)


def test_should_alert_when_price_is_below_or_equal_limit() -> None:
    assert should_alert(make_fare(total_price=1000.0), make_monitor()) is True
    assert should_alert(make_fare(total_price=900.0), make_monitor()) is True


def test_should_not_alert_when_price_is_above_limit() -> None:
    assert should_alert(make_fare(total_price=1000.01), make_monitor()) is False


def test_should_not_alert_when_currency_differs() -> None:
    assert should_alert(make_fare(currency="USD"), make_monitor(currency="BRL")) is False


def test_should_not_alert_when_stops_exceed_maximum() -> None:
    assert should_alert(make_fare(stops=2), make_monitor(max_stops=1)) is False


def test_should_not_alert_when_stops_are_missing_and_monitor_has_limit() -> None:
    assert should_alert(make_fare(stops=None), make_monitor(max_stops=1)) is False


def test_should_not_alert_when_monitor_is_inactive() -> None:
    assert should_alert(make_fare(), make_monitor(status="inactive")) is False


def test_alert_hash_is_stable() -> None:
    monitor = make_monitor()
    fare = make_fare()

    assert generate_alert_hash(fare, monitor) == generate_alert_hash(fare, monitor)


def test_alert_hash_changes_for_different_logical_offer() -> None:
    monitor = make_monitor()

    assert generate_alert_hash(make_fare(total_price=900), monitor) != generate_alert_hash(
        make_fare(total_price=950),
        monitor,
    )
