"""Thin persistence service for runtime and backtest integrations."""

from pathlib import Path
from uuid import uuid4

from loguru import logger

from app.analytics.models import AnalyticsSnapshot, TradeJournalEntry
from app.brokers.health import BrokerHealthSnapshot
from app.risk.models import RiskEvent
from app.runtime.runtime_state import RuntimeState
from app.storage.event_store import EventStore
from app.storage.models import (
    StoredAnalyticsSnapshot,
    StoredBrokerHealthEvent,
    StoredEvent,
    StoredRiskEvent,
    StoredTrade,
    utc_now,
)
from app.storage.repositories import (
    AnalyticsRepository,
    BrokerHealthRepository,
    RiskRepository,
    RuntimeRepository,
    TradeRepository,
)
from app.storage.session import StorageSession
from app.storage.snapshots import SnapshotManager


class PersistenceService:
    """Coordinates optional durable persistence without owning domain logic."""

    def __init__(
        self,
        database_path: Path | str = "storage/trading_system.db",
        session_id: str | None = None,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self.session = StorageSession.create(database_path, session_id=session_id)
        connection = self.session.database.get_connection()
        self.events = EventStore(connection)
        self.trades = TradeRepository(connection)
        self.risk = RiskRepository(connection)
        self.analytics = AnalyticsRepository(connection)
        self.runtime = RuntimeRepository(connection)
        self.broker_health = BrokerHealthRepository(connection)
        self.snapshots = SnapshotManager(self.runtime)

    @property
    def session_id(self) -> str:
        """Return logical persistence session id."""
        return self.session.session_id

    def persist_trade_journal(self, entries: list[TradeJournalEntry]) -> None:
        """Persist trade journal entries and matching execution events."""
        if not self.enabled:
            return
        for entry in entries:
            trade = StoredTrade(
                trade_id=entry.trade_id,
                session_id=self.session_id,
                strategy_name=entry.strategy_name,
                symbol=entry.symbol,
                timeframe=entry.timeframe,
                direction=entry.direction,
                lifecycle_state=entry.lifecycle_state,
                timestamp=entry.timestamp,
                confidence=entry.confidence,
                pnl=entry.pnl,
                outcome=entry.outcome,
                rejection_reason=entry.rejection_reason,
            )
            self.trades.add(trade)
            self.events.append(
                StoredEvent(
                    session_id=self.session_id,
                    event_type=f"execution.{entry.lifecycle_state}",
                    aggregate_id=entry.trade_id,
                    timestamp=entry.timestamp,
                    payload=entry.to_dict(),
                )
            )

    def persist_risk_events(self, events: list[RiskEvent]) -> None:
        """Persist risk validation events."""
        if not self.enabled:
            return
        for event in events:
            reason = event.reason.value if event.reason else None
            stored = StoredRiskEvent(
                event_id=str(uuid4()),
                session_id=self.session_id,
                timestamp=event.timestamp,
                strategy_name=event.strategy_name,
                symbol=event.symbol,
                timeframe=event.timeframe,
                approved=event.approved,
                reason=reason,
                message=event.message,
                state_snapshot=event.state_snapshot,
            )
            self.risk.add(stored)
            self.events.append(
                StoredEvent(
                    session_id=self.session_id,
                    event_type="risk.validation",
                    aggregate_id=f"{event.strategy_name}:{event.symbol}",
                    timestamp=event.timestamp,
                    payload=event.to_dict(),
                )
            )

    def persist_analytics_snapshot(
        self,
        snapshot: AnalyticsSnapshot,
        snapshot_type: str,
    ) -> None:
        """Persist an analytics snapshot."""
        if not self.enabled:
            return
        stored = StoredAnalyticsSnapshot(
            snapshot_id=str(uuid4()),
            session_id=self.session_id,
            timestamp=snapshot.generated_at,
            snapshot_type=snapshot_type,
            payload=snapshot.to_dict(),
        )
        self.analytics.add_snapshot(stored)
        self.events.append(
            StoredEvent(
                session_id=self.session_id,
                event_type="analytics.snapshot",
                aggregate_id=stored.snapshot_id,
                timestamp=snapshot.generated_at,
                payload=stored.payload,
            )
        )

    def persist_runtime_state(self, state: RuntimeState) -> None:
        """Persist a runtime state event."""
        if not self.enabled:
            return
        payload = state.snapshot()
        self.events.append(
            StoredEvent(
                session_id=self.session_id,
                event_type="runtime.state",
                aggregate_id=self.session_id,
                timestamp=utc_now(),
                payload=payload,
            )
        )

    def persist_broker_health(self, broker_name: str, health: BrokerHealthSnapshot) -> None:
        """Persist broker health event."""
        if not self.enabled:
            return
        timestamp = health.last_heartbeat or utc_now()
        stored = StoredBrokerHealthEvent(
            event_id=str(uuid4()),
            session_id=self.session_id,
            timestamp=timestamp,
            broker_name=broker_name,
            status=health.status.value,
            connected=health.connected,
            payload=health.to_dict(),
        )
        self.broker_health.add(stored)
        self.events.append(
            StoredEvent(
                session_id=self.session_id,
                event_type="broker.health",
                aggregate_id=broker_name,
                timestamp=timestamp,
                payload=health.to_dict(),
            )
        )

    def persist_stream_event(
        self,
        event_type: str,
        aggregate_id: str,
        payload: dict[str, object],
    ) -> None:
        """Persist a stream lifecycle or replay metadata event."""
        if not self.enabled:
            return
        self.events.append(
            StoredEvent(
                session_id=self.session_id,
                event_type=event_type,
                aggregate_id=aggregate_id,
                timestamp=utc_now(),
                payload=payload,
            )
        )

    def persist_stream_health(self, source: str, payload: dict[str, object]) -> None:
        """Persist a stream health snapshot."""
        self.persist_stream_event("stream.health", source, payload)

    def persist_stream_validation_failure(
        self,
        source: str,
        payload: dict[str, object],
    ) -> None:
        """Persist a stream validation failure without storing raw ticks by default."""
        self.persist_stream_event("stream.validation_failure", source, payload)

    def persist_external_feed_snapshot(self, source: str, payload: dict[str, object]) -> None:
        """Persist an external feed health snapshot."""
        self.persist_stream_event("external_data.feed_snapshot", source, payload)

    def persist_external_quality_report(self, source: str, payload: dict[str, object]) -> None:
        """Persist an external feed quality report."""
        self.persist_stream_event("external_data.quality_report", source, payload)

    def persist_external_latency_metrics(self, source: str, payload: dict[str, object]) -> None:
        """Persist external feed latency metrics."""
        self.persist_stream_event("external_data.latency_metrics", source, payload)

    def persist_external_feed_incident(self, source: str, payload: dict[str, object]) -> None:
        """Persist an external feed incident."""
        self.persist_stream_event("external_data.incident", source, payload)

    def close(self) -> None:
        """Close persistence resources."""
        logger.bind(component="storage").info("Persistence service closed")
        self.session.close()
