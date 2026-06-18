from hashlib import sha256

from app.models import FareResult, Monitor


def should_alert(fare: FareResult, monitor: Monitor) -> bool:
    if monitor.status != "active":
        return False

    if fare.currency.upper() != monitor.currency.upper():
        return False

    if fare.total_price > monitor.max_price:
        return False

    if monitor.max_stops is not None and fare.stops is None:
        return False

    if monitor.max_stops is not None:
        return fare.stops <= monitor.max_stops

    return True


def generate_alert_hash(fare: FareResult, monitor: Monitor) -> str:
    parts = [
        str(monitor.id or ""),
        monitor.origin.upper(),
        monitor.destination.upper(),
        monitor.departure_date,
        monitor.return_date or "",
        fare.source.lower(),
        fare.airline or "",
        f"{fare.total_price:.2f}",
        fare.currency.upper(),
        str(fare.stops if fare.stops is not None else ""),
        fare.departure_at or "",
        fare.return_at or "",
    ]
    return sha256("|".join(parts).encode("utf-8")).hexdigest()
