"""Replay engine for stored sessions and event timelines."""

from dataclasses import dataclass

from loguru import logger

from app.storage.event_store import EventStore
from app.storage.models import StoredEvent
from app.storage.repositories import TradeRepository


@dataclass(frozen=True)
class ReplayResult:
    """Reconstructed replay result."""

    session_id: str
    events: list[StoredEvent]
    reconstructed_state: dict[str, object]


class ReplayEngine:
    """Replays stored events into a lightweight reconstructed state."""

    def __init__(self, event_store: EventStore, trade_repository: TradeRepository) -> None:
        self.event_store = event_store
        self.trade_repository = trade_repository

    def replay_session(self, session_id: str) -> ReplayResult:
        """Replay a full session timeline."""
        events = self.event_store.replay(session_id=session_id)
        state: dict[str, object] = {
            "session_id": session_id,
            "event_count": len(events),
            "execution_events": 0,
            "risk_events": 0,
            "broker_events": 0,
            "analytics_events": 0,
        }
        for event in events:
            if event.event_type.startswith("execution."):
                state["execution_events"] = int(state["execution_events"]) + 1
            elif event.event_type.startswith("risk."):
                state["risk_events"] = int(state["risk_events"]) + 1
            elif event.event_type.startswith("broker."):
                state["broker_events"] = int(state["broker_events"]) + 1
            elif event.event_type.startswith("analytics."):
                state["analytics_events"] = int(state["analytics_events"]) + 1
        logger.bind(component="storage").info(
            "Session replay completed session={} events={}",
            session_id,
            len(events),
        )
        return ReplayResult(session_id=session_id, events=events, reconstructed_state=state)

    def replay_trades(self, session_id: str) -> dict[str, object]:
        """Replay trade lifecycle records."""
        trades = self.trade_repository.list(session_id=session_id, limit=10_000)
        return {
            "session_id": session_id,
            "trade_events": len(trades),
            "settled": sum(1 for trade in trades if trade.lifecycle_state == "settled"),
            "blocked": sum(1 for trade in trades if trade.lifecycle_state == "blocked"),
        }

    def replay_risk(self, session_id: str) -> dict[str, object]:
        """Replay risk events from the event store."""
        risk_events = self.event_store.replay(session_id=session_id, event_type="risk.validation")
        return {"session_id": session_id, "risk_events": len(risk_events)}
