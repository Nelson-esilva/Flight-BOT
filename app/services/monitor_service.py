from collections.abc import Callable
from sqlite3 import Connection, Row

from app.database import connect, initialize_database
from app.models import AlertSent, FareResult, Monitor
from app.rules import generate_alert_hash, should_alert
from app.schemas import MonitorCreate, MonitorUpdate
from app.services.amadeus_client import search_flight_offers
from app.services.telegram_notifier import send_alert


FlightOfferSearch = Callable[[Monitor], list[FareResult]]
AlertSender = Callable[[Monitor, FareResult], None]


class MonitorRunResult:
    def __init__(
        self,
        monitor: Monitor | None,
        offers: list[FareResult],
        best_offer: FareResult | None,
        alerts_sent: int = 0,
        duplicate_alerts: int = 0,
        alert_error: str | None = None,
    ) -> None:
        self.monitor = monitor
        self.offers = offers
        self.best_offer = best_offer
        self.alerts_sent = alerts_sent
        self.duplicate_alerts = duplicate_alerts
        self.alert_error = alert_error


def _monitor_from_row(row: Row) -> Monitor:
    return Monitor(
        id=row["id"],
        origin=row["origin"],
        destination=row["destination"],
        departure_date=row["departure_date"],
        return_date=row["return_date"],
        trip_type=row["trip_type"],
        max_price=row["max_price"],
        currency=row["currency"],
        adults=row["adults"],
        max_stops=row["max_stops"],
        status=row["status"],
    )


def _fare_result_from_row(row: Row) -> FareResult:
    return FareResult(
        id=row["id"],
        monitor_id=row["monitor_id"],
        source=row["source"],
        airline=row["airline"],
        total_price=row["total_price"],
        currency=row["currency"],
        stops=row["stops"],
        duration=row["duration"],
        departure_at=row["departure_at"],
        return_at=row["return_at"],
        raw_json=row["raw_json"],
    )


def _alert_sent_from_row(row: Row) -> AlertSent:
    return AlertSent(
        id=row["id"],
        monitor_id=row["monitor_id"],
        fare_result_id=row["fare_result_id"],
        alert_hash=row["alert_hash"],
    )


def create_monitor(data: MonitorCreate, connection: Connection | None = None) -> Monitor:
    owns_connection = connection is None
    db = connection or connect()
    initialize_database(db)

    try:
        cursor = db.execute(
            """
            INSERT INTO monitors (
                origin,
                destination,
                departure_date,
                return_date,
                trip_type,
                max_price,
                currency,
                adults,
                max_stops,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """,
            (
                data.origin,
                data.destination,
                data.departure_date.isoformat(),
                data.return_date.isoformat() if data.return_date else None,
                data.trip_type,
                data.max_price,
                data.currency,
                data.adults,
                data.max_stops,
            ),
        )
        db.commit()
        created = get_monitor(cursor.lastrowid, db)
        if created is None:
            raise RuntimeError("created monitor could not be loaded")
        return created
    finally:
        if owns_connection:
            db.close()


def list_monitors(connection: Connection | None = None) -> list[Monitor]:
    owns_connection = connection is None
    db = connection or connect()
    initialize_database(db)

    try:
        rows = db.execute(
            """
            SELECT
                id,
                origin,
                destination,
                departure_date,
                return_date,
                trip_type,
                max_price,
                currency,
                adults,
                max_stops,
                status
            FROM monitors
            ORDER BY id
            """
        ).fetchall()
        return [_monitor_from_row(row) for row in rows]
    finally:
        if owns_connection:
            db.close()


def get_monitor(monitor_id: int, connection: Connection | None = None) -> Monitor | None:
    owns_connection = connection is None
    db = connection or connect()
    initialize_database(db)

    try:
        row = db.execute(
            """
            SELECT
                id,
                origin,
                destination,
                departure_date,
                return_date,
                trip_type,
                max_price,
                currency,
                adults,
                max_stops,
                status
            FROM monitors
            WHERE id = ?
            """,
            (monitor_id,),
        ).fetchone()

        if row is None:
            return None

        return _monitor_from_row(row)
    finally:
        if owns_connection:
            db.close()


def update_monitor_status(
    monitor_id: int,
    data: MonitorUpdate,
    connection: Connection | None = None,
) -> Monitor | None:
    owns_connection = connection is None
    db = connection or connect()
    initialize_database(db)

    try:
        cursor = db.execute(
            """
            UPDATE monitors
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (data.status, monitor_id),
        )
        db.commit()

        if cursor.rowcount == 0:
            return None

        return get_monitor(monitor_id, db)
    finally:
        if owns_connection:
            db.close()


def delete_monitor(monitor_id: int, connection: Connection | None = None) -> bool:
    owns_connection = connection is None
    db = connection or connect()
    initialize_database(db)

    try:
        cursor = db.execute("DELETE FROM monitors WHERE id = ?", (monitor_id,))
        db.commit()
        return cursor.rowcount > 0
    finally:
        if owns_connection:
            db.close()


def save_fare_result(
    fare: FareResult,
    connection: Connection | None = None,
) -> FareResult:
    owns_connection = connection is None
    db = connection or connect()
    initialize_database(db)

    try:
        cursor = db.execute(
            """
            INSERT INTO fare_results (
                monitor_id,
                source,
                airline,
                total_price,
                currency,
                stops,
                duration,
                departure_at,
                return_at,
                raw_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fare.monitor_id,
                fare.source,
                fare.airline,
                fare.total_price,
                fare.currency,
                fare.stops,
                fare.duration,
                fare.departure_at,
                fare.return_at,
                fare.raw_json,
            ),
        )
        db.commit()
        saved = get_fare_result(cursor.lastrowid, db)
        if saved is None:
            raise RuntimeError("saved fare result could not be loaded")
        return saved
    finally:
        if owns_connection:
            db.close()


def get_fare_result(
    fare_result_id: int,
    connection: Connection | None = None,
) -> FareResult | None:
    owns_connection = connection is None
    db = connection or connect()
    initialize_database(db)

    try:
        row = db.execute(
            """
            SELECT
                id,
                monitor_id,
                source,
                airline,
                total_price,
                currency,
                stops,
                duration,
                departure_at,
                return_at,
                raw_json
            FROM fare_results
            WHERE id = ?
            """,
            (fare_result_id,),
        ).fetchone()

        if row is None:
            return None

        return _fare_result_from_row(row)
    finally:
        if owns_connection:
            db.close()


def list_fare_results_for_monitor(
    monitor_id: int,
    connection: Connection | None = None,
) -> list[FareResult]:
    owns_connection = connection is None
    db = connection or connect()
    initialize_database(db)

    try:
        rows = db.execute(
            """
            SELECT
                id,
                monitor_id,
                source,
                airline,
                total_price,
                currency,
                stops,
                duration,
                departure_at,
                return_at,
                raw_json
            FROM fare_results
            WHERE monitor_id = ?
            ORDER BY id
            """,
            (monitor_id,),
        ).fetchall()
        return [_fare_result_from_row(row) for row in rows]
    finally:
        if owns_connection:
            db.close()


def run_monitor_now(
    monitor_id: int,
    connection: Connection | None = None,
    offer_search: FlightOfferSearch = search_flight_offers,
    alert_sender: AlertSender = send_alert,
) -> MonitorRunResult:
    owns_connection = connection is None
    db = connection or connect()
    initialize_database(db)

    try:
        monitor = get_monitor(monitor_id, db)
        if monitor is None:
            return MonitorRunResult(None, [], None)

        if monitor.status != "active":
            return MonitorRunResult(monitor, [], None)

        offers = offer_search(monitor)
        saved_offers = [save_fare_result(offer, db) for offer in offers]
        best_offer = min(saved_offers, key=lambda offer: offer.total_price, default=None)
        alerts_sent, duplicate_alerts, alert_error = process_alerts(
            monitor,
            saved_offers,
            db,
            alert_sender,
        )
        return MonitorRunResult(
            monitor,
            saved_offers,
            best_offer,
            alerts_sent,
            duplicate_alerts,
            alert_error,
        )
    finally:
        if owns_connection:
            db.close()


def alert_was_sent(alert_hash: str, connection: Connection | None = None) -> bool:
    owns_connection = connection is None
    db = connection or connect()
    initialize_database(db)

    try:
        row = db.execute(
            "SELECT 1 FROM alerts_sent WHERE alert_hash = ?",
            (alert_hash,),
        ).fetchone()
        return row is not None
    finally:
        if owns_connection:
            db.close()


def register_alert_sent(
    monitor: Monitor,
    fare: FareResult,
    connection: Connection | None = None,
) -> AlertSent:
    owns_connection = connection is None
    db = connection or connect()
    initialize_database(db)
    alert_hash = generate_alert_hash(fare, monitor)

    try:
        existing = get_alert_sent(alert_hash, db)
        if existing is not None:
            return existing

        cursor = db.execute(
            """
            INSERT INTO alerts_sent (
                monitor_id,
                fare_result_id,
                alert_hash
            )
            VALUES (?, ?, ?)
            """,
            (monitor.id, fare.id, alert_hash),
        )
        db.commit()

        created = get_alert_sent(alert_hash, db)
        if created is None:
            raise RuntimeError("created alert record could not be loaded")
        return created
    finally:
        if owns_connection:
            db.close()


def get_alert_sent(
    alert_hash: str,
    connection: Connection | None = None,
) -> AlertSent | None:
    owns_connection = connection is None
    db = connection or connect()
    initialize_database(db)

    try:
        row = db.execute(
            """
            SELECT
                id,
                monitor_id,
                fare_result_id,
                alert_hash
            FROM alerts_sent
            WHERE alert_hash = ?
            """,
            (alert_hash,),
        ).fetchone()

        if row is None:
            return None

        return _alert_sent_from_row(row)
    finally:
        if owns_connection:
            db.close()


def should_send_new_alert(
    monitor: Monitor,
    fare: FareResult,
    connection: Connection | None = None,
) -> bool:
    return not alert_was_sent(generate_alert_hash(fare, monitor), connection)


def process_alerts(
    monitor: Monitor,
    fares: list[FareResult],
    connection: Connection | None = None,
    alert_sender: AlertSender = send_alert,
) -> tuple[int, int, str | None]:
    owns_connection = connection is None
    db = connection or connect()
    initialize_database(db)
    sent_count = 0
    duplicate_count = 0
    alert_error: str | None = None

    try:
        for fare in fares:
            if not should_alert(fare, monitor):
                continue

            if not should_send_new_alert(monitor, fare, db):
                duplicate_count += 1
                continue

            try:
                alert_sender(monitor, fare)
            except Exception as exc:
                alert_error = str(exc)
                continue

            register_alert_sent(monitor, fare, db)
            sent_count += 1

        return sent_count, duplicate_count, alert_error
    finally:
        if owns_connection:
            db.close()
