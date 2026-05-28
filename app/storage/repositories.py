"""Repository layer for typed storage operations."""

import json
from collections.abc import Iterable
from datetime import datetime
from sqlite3 import Connection, Row
from typing import Any

from loguru import logger

from app.storage.models import (
    StoredAnalyticsSnapshot,
    StoredBrokerHealthEvent,
    StoredExecutionEvent,
    StoredRiskEvent,
    StoredRuntimeEvent,
    StoredRuntimeState,
    StoredSignal,
    StoredTrade,
)


def _dumps(payload: dict[str, Any]) -> str:
    return json.dumps(payload, default=str)


def _loads(payload: str) -> dict[str, Any]:
    return json.loads(payload)


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


class BaseRepository:
    """Base repository with shared pagination helpers."""

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def _limit_offset(self, limit: int, offset: int) -> tuple[int, int]:
        return max(1, limit), max(0, offset)


class TradeRepository(BaseRepository):
    """Repository for persisted trade lifecycle records."""

    def add(self, trade: StoredTrade) -> None:
        """Persist a trade lifecycle record."""
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO trades (
                    trade_id, session_id, strategy_name, symbol, timeframe, direction,
                    lifecycle_state, timestamp, confidence, pnl, outcome, rejection_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trade.trade_id,
                    trade.session_id,
                    trade.strategy_name,
                    trade.symbol,
                    trade.timeframe,
                    trade.direction,
                    trade.lifecycle_state,
                    trade.timestamp.isoformat(),
                    trade.confidence,
                    trade.pnl,
                    trade.outcome,
                    trade.rejection_reason,
                ),
            )
        logger.bind(component="storage").info("Trade persisted {}", trade.trade_id)

    def list(
        self,
        session_id: str | None = None,
        symbol: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[StoredTrade]:
        """List trades with optional filters."""
        limit, offset = self._limit_offset(limit, offset)
        query = "SELECT * FROM trades WHERE 1=1"
        params: list[Any] = []
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        query += " ORDER BY timestamp LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        return [self._from_row(row) for row in self.connection.execute(query, params)]

    def _from_row(self, row: Row) -> StoredTrade:
        return StoredTrade(
            trade_id=str(row["trade_id"]),
            session_id=str(row["session_id"]),
            strategy_name=str(row["strategy_name"]),
            symbol=str(row["symbol"]),
            timeframe=str(row["timeframe"]),
            direction=str(row["direction"]),
            lifecycle_state=str(row["lifecycle_state"]),
            timestamp=_dt(str(row["timestamp"])),
            confidence=float(row["confidence"]),
            pnl=float(row["pnl"]),
            outcome=row["outcome"],
            rejection_reason=row["rejection_reason"],
        )


class SignalRepository(BaseRepository):
    """Repository for generated signals."""

    def add(self, signal: StoredSignal) -> None:
        """Persist a signal."""
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO signals (
                    signal_id, session_id, strategy_name, symbol, timeframe,
                    direction, confidence, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    signal.signal_id,
                    signal.session_id,
                    signal.strategy_name,
                    signal.symbol,
                    signal.timeframe,
                    signal.direction,
                    signal.confidence,
                    signal.timestamp.isoformat(),
                ),
            )

    def list(self, session_id: str | None = None, limit: int = 100) -> list[StoredSignal]:
        """List persisted signals."""
        query = "SELECT * FROM signals"
        params: list[Any] = []
        if session_id:
            query += " WHERE session_id = ?"
            params.append(session_id)
        query += " ORDER BY timestamp LIMIT ?"
        params.append(max(1, limit))
        return [
            StoredSignal(
                signal_id=str(row["signal_id"]),
                session_id=str(row["session_id"]),
                strategy_name=str(row["strategy_name"]),
                symbol=str(row["symbol"]),
                timeframe=str(row["timeframe"]),
                direction=str(row["direction"]),
                confidence=float(row["confidence"]),
                timestamp=_dt(str(row["timestamp"])),
            )
            for row in self.connection.execute(query, params)
        ]


class RuntimeRepository(BaseRepository):
    """Repository for runtime state and runtime events."""

    def add_event(self, event: StoredRuntimeEvent) -> None:
        """Persist a runtime event."""
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO runtime_events (
                    event_id, session_id, event_type, timestamp, message, payload
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.session_id,
                    event.event_type,
                    event.timestamp.isoformat(),
                    event.message,
                    _dumps(event.payload),
                ),
            )

    def add_state(self, state: StoredRuntimeState) -> None:
        """Persist a runtime state snapshot."""
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO runtime_states (
                    state_id, session_id, timestamp, mode, active, health, payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.state_id,
                    state.session_id,
                    state.timestamp.isoformat(),
                    state.mode,
                    int(state.active),
                    state.health,
                    _dumps(state.payload),
                ),
            )

    def latest_state(self, session_id: str) -> StoredRuntimeState | None:
        """Return the latest runtime state snapshot for a session."""
        row = self.connection.execute(
            """
            SELECT * FROM runtime_states
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        return StoredRuntimeState(
            state_id=str(row["state_id"]),
            session_id=str(row["session_id"]),
            timestamp=_dt(str(row["timestamp"])),
            mode=str(row["mode"]),
            active=bool(row["active"]),
            health=str(row["health"]),
            payload=_loads(str(row["payload"])),
        )


class AnalyticsRepository(BaseRepository):
    """Repository for analytics snapshots."""

    def add_snapshot(self, snapshot: StoredAnalyticsSnapshot) -> None:
        """Persist an analytics snapshot."""
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO analytics_snapshots (
                    snapshot_id, session_id, timestamp, snapshot_type, payload
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    snapshot.snapshot_id,
                    snapshot.session_id,
                    snapshot.timestamp.isoformat(),
                    snapshot.snapshot_type,
                    _dumps(snapshot.payload),
                ),
            )

    def list_snapshots(self, session_id: str | None = None) -> list[StoredAnalyticsSnapshot]:
        """List analytics snapshots."""
        query = "SELECT * FROM analytics_snapshots"
        params: list[Any] = []
        if session_id:
            query += " WHERE session_id = ?"
            params.append(session_id)
        query += " ORDER BY timestamp"
        return [
            StoredAnalyticsSnapshot(
                snapshot_id=str(row["snapshot_id"]),
                session_id=str(row["session_id"]),
                timestamp=_dt(str(row["timestamp"])),
                snapshot_type=str(row["snapshot_type"]),
                payload=_loads(str(row["payload"])),
            )
            for row in self.connection.execute(query, params)
        ]


class RiskRepository(BaseRepository):
    """Repository for risk validation events."""

    def add(self, event: StoredRiskEvent) -> None:
        """Persist a risk event."""
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO risk_events (
                    event_id, session_id, timestamp, strategy_name, symbol,
                    timeframe, approved, reason, message, state_snapshot
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.session_id,
                    event.timestamp.isoformat(),
                    event.strategy_name,
                    event.symbol,
                    event.timeframe,
                    int(event.approved),
                    event.reason,
                    event.message,
                    _dumps(event.state_snapshot),
                ),
            )

    def add_many(self, events: Iterable[StoredRiskEvent]) -> None:
        """Persist multiple risk events."""
        for event in events:
            self.add(event)


class BrokerHealthRepository(BaseRepository):
    """Repository for broker health events."""

    def add(self, event: StoredBrokerHealthEvent) -> None:
        """Persist a broker health event."""
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO broker_health_events (
                    event_id, session_id, timestamp, broker_name, status, connected, payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.session_id,
                    event.timestamp.isoformat(),
                    event.broker_name,
                    event.status,
                    int(event.connected),
                    _dumps(event.payload),
                ),
            )


class ExecutionRepository(BaseRepository):
    """Repository for execution lifecycle events."""

    def add(self, event: StoredExecutionEvent) -> None:
        """Persist an execution event."""
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO execution_events (
                    event_id, session_id, timestamp, trade_id, lifecycle_state, payload
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.session_id,
                    event.timestamp.isoformat(),
                    event.trade_id,
                    event.lifecycle_state,
                    _dumps(event.payload),
                ),
            )
