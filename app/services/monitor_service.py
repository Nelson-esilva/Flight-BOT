from sqlite3 import Connection, Row

from app.database import connect, initialize_database
from app.models import Monitor
from app.schemas import MonitorCreate, MonitorUpdate


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
