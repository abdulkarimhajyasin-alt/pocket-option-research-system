"""Run local SQLite storage diagnostics."""

from pathlib import Path
import sys
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loguru import logger  # noqa: E402

from app.config.settings import Settings  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402
from app.runtime.recovery import RecoveryManager  # noqa: E402
from app.runtime.runtime_state import RuntimeMode, RuntimeState  # noqa: E402
from app.risk.risk_engine import RiskEngine  # noqa: E402
from app.storage.event_store import EventStore  # noqa: E402
from app.storage.migrations import list_tables  # noqa: E402
from app.storage.models import StoredEvent, StoredRuntimeEvent, StoredTrade, utc_now  # noqa: E402
from app.storage.replay import ReplayEngine  # noqa: E402
from app.storage.repositories import RuntimeRepository, TradeRepository  # noqa: E402
from app.storage.session import StorageSession  # noqa: E402
from app.storage.snapshots import SnapshotManager  # noqa: E402


def main() -> None:
    """Initialize storage, insert sample records, replay, and recover."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)

    session_id = f"storage_check_{uuid4()}"
    storage = StorageSession.create(
        PROJECT_ROOT / "storage" / "trading_system.db",
        session_id=session_id,
    )
    connection = storage.database.get_connection()
    trade_repository = TradeRepository(connection)
    runtime_repository = RuntimeRepository(connection)
    event_store = EventStore(connection)

    timestamp = utc_now()
    trade_repository.add(
        StoredTrade(
            trade_id="diagnostic_trade",
            session_id=session_id,
            strategy_name="diagnostic",
            symbol="EURUSD",
            timeframe="1m",
            direction="call",
            lifecycle_state="settled",
            timestamp=timestamp,
            confidence=0.9,
            pnl=0.8,
            outcome="win",
        )
    )
    runtime_repository.add_event(
        StoredRuntimeEvent(
            event_id=str(uuid4()),
            session_id=session_id,
            event_type="diagnostic",
            timestamp=timestamp,
            message="storage diagnostic event",
            payload={"ok": True},
        )
    )
    event_store.append(
        StoredEvent(
            session_id=session_id,
            event_type="execution.settled",
            aggregate_id="diagnostic_trade",
            timestamp=timestamp,
            payload={"pnl": 0.8},
        )
    )

    runtime_state = RuntimeState(mode=RuntimeMode.PAPER)
    runtime_state.start()
    risk_engine = RiskEngine()
    snapshot_manager = SnapshotManager(runtime_repository)
    snapshot_manager.create_snapshot(session_id, runtime_state, risk_engine, [])
    replay = ReplayEngine(event_store, trade_repository).replay_session(session_id)
    recovery = RecoveryManager(snapshot_manager).recover(session_id)
    tables = list_tables(connection)
    storage.close()

    diagnostics = {
        "session_id": session_id,
        "tables": tables,
        "replay": replay.reconstructed_state,
        "recovery": {
            "recovered": recovery.recovered,
            "message": recovery.message,
        },
    }
    logger.info("Storage diagnostics: {}", diagnostics)
    print(diagnostics)


if __name__ == "__main__":
    main()
