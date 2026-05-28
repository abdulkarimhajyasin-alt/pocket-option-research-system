"""Append-only event store with replay support."""

import json
from datetime import datetime
from sqlite3 import Connection, Row
from typing import Any

from loguru import logger

from app.storage.models import StoredEvent


class EventStore:
    """Stores append-only events and returns ordered timelines for replay."""

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def append(self, event: StoredEvent) -> None:
        """Append a typed storage event."""
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO events (
                    event_id, session_id, event_type, aggregate_id, timestamp, payload
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.session_id,
                    event.event_type,
                    event.aggregate_id,
                    event.timestamp.isoformat(),
                    json.dumps(event.payload, default=str),
                ),
            )
        logger.bind(component="storage").info(
            "Event appended type={} aggregate={}",
            event.event_type,
            event.aggregate_id,
        )

    def replay(
        self,
        session_id: str | None = None,
        event_type: str | None = None,
    ) -> list[StoredEvent]:
        """Return events in append timestamp order."""
        query = "SELECT * FROM events WHERE 1=1"
        params: list[Any] = []
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        query += " ORDER BY timestamp"
        rows = self.connection.execute(query, params).fetchall()
        logger.bind(component="storage").info("Replay loaded {} events", len(rows))
        return [self._from_row(row) for row in rows]

    def _from_row(self, row: Row) -> StoredEvent:
        return StoredEvent(
            event_id=str(row["event_id"]),
            session_id=str(row["session_id"]),
            event_type=str(row["event_type"]),
            aggregate_id=str(row["aggregate_id"]),
            timestamp=datetime.fromisoformat(str(row["timestamp"])),
            payload=json.loads(str(row["payload"])),
        )
