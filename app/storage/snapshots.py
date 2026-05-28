"""Runtime snapshot persistence and restoration helpers."""

from dataclasses import dataclass
from uuid import uuid4

from loguru import logger

from app.risk.risk_engine import RiskEngine
from app.runtime.runtime_state import RuntimeState
from app.storage.models import StoredRuntimeState, utc_now
from app.storage.repositories import RuntimeRepository


@dataclass(frozen=True)
class RuntimeSnapshot:
    """Recovery-safe snapshot of runtime, risk, and positions."""

    session_id: str
    runtime_state: dict[str, object]
    risk_state: dict[str, object]
    open_positions: list[dict[str, object]]


class SnapshotManager:
    """Creates and restores runtime snapshots."""

    def __init__(self, runtime_repository: RuntimeRepository) -> None:
        self.runtime_repository = runtime_repository

    def create_snapshot(
        self,
        session_id: str,
        runtime_state: RuntimeState,
        risk_engine: RiskEngine,
        open_positions: list[object],
    ) -> RuntimeSnapshot:
        """Persist and return a runtime snapshot."""
        position_payload = [
            getattr(position, "__dict__", {"value": str(position)}) for position in open_positions
        ]
        payload = {
            "runtime_state": runtime_state.snapshot(),
            "risk_state": risk_engine.state_snapshot(),
            "open_positions": position_payload,
        }
        stored = StoredRuntimeState(
            state_id=str(uuid4()),
            session_id=session_id,
            timestamp=utc_now(),
            mode=str(payload["runtime_state"].get("mode")),
            active=bool(payload["runtime_state"].get("active")),
            health=str(payload["runtime_state"].get("health")),
            payload=payload,
        )
        self.runtime_repository.add_state(stored)
        logger.bind(component="storage").info("Runtime snapshot created session={}", session_id)
        return RuntimeSnapshot(
            session_id=session_id,
            runtime_state=payload["runtime_state"],
            risk_state=payload["risk_state"],
            open_positions=position_payload,
        )

    def restore_latest(self, session_id: str) -> RuntimeSnapshot | None:
        """Restore the latest persisted runtime snapshot."""
        stored = self.runtime_repository.latest_state(session_id)
        if stored is None:
            return None
        payload = stored.payload
        logger.bind(component="storage").info("Runtime snapshot restored session={}", session_id)
        return RuntimeSnapshot(
            session_id=session_id,
            runtime_state=dict(payload.get("runtime_state", {})),
            risk_state=dict(payload.get("risk_state", {})),
            open_positions=list(payload.get("open_positions", [])),
        )
