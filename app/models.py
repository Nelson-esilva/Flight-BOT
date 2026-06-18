from dataclasses import dataclass


@dataclass(slots=True)
class Monitor:
    id: int | None
    origin: str
    destination: str
    departure_date: str
    return_date: str | None
    trip_type: str
    max_price: float
    currency: str = "BRL"
    adults: int = 1
    max_stops: int | None = None
    status: str = "active"


@dataclass(slots=True)
class FareResult:
    id: int | None
    monitor_id: int
    source: str
    total_price: float
    currency: str
    airline: str | None = None
    stops: int | None = None
    duration: str | None = None
    departure_at: str | None = None
    return_at: str | None = None
    raw_json: str | None = None


@dataclass(slots=True)
class AlertSent:
    id: int | None
    monitor_id: int
    alert_hash: str
    fare_result_id: int | None = None
