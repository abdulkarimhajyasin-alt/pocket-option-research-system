"""Tests for persistence, storage, replay, and recovery infrastructure."""

from uuid import uuid4

from app.analytics.models import TradeJournalEntry
from app.runtime.recovery import RecoveryManager
from app.runtime.runtime_state import RuntimeMode, RuntimeState
from app.risk.risk_engine import RiskEngine
from app.signals.signal import SignalDirection
from app.storage.event_store import EventStore
from app.storage.migrations import list_tables
from app.storage.models import StoredEvent, StoredTrade, utc_now
from app.storage.persistence import PersistenceService
from app.storage.replay import ReplayEngine
from app.storage.repositories import RuntimeRepository, TradeRepository
from app.storage.session import StorageSession
from app.storage.snapshots import SnapshotManager


def test_schema_initialization_creates_tables(tmp_path) -> None:
    storage = StorageSession.create(tmp_path / "test.db")
    tables = set(list_tables(storage.database.get_connection()))
    storage.close()

    assert "events" in tables
    assert "trades" in tables
    assert "runtime_states" in tables


def test_trade_repository_filters_and_paginates(tmp_path) -> None:
    storage = StorageSession.create(tmp_path / "test.db", session_id="s1")
    repo = TradeRepository(storage.database.get_connection())
    repo.add(
        StoredTrade(
            trade_id="t1",
            session_id="s1",
            strategy_name="sample",
            symbol="EURUSD",
            timeframe="1m",
            direction="call",
            lifecycle_state="settled",
            timestamp=utc_now(),
            confidence=0.8,
        )
    )

    trades = repo.list(session_id="s1", symbol="EURUSD", limit=10)
    storage.close()

    assert len(trades) == 1
    assert trades[0].trade_id == "t1"


def test_event_store_and_replay_engine(tmp_path) -> None:
    storage = StorageSession.create(tmp_path / "test.db", session_id="s1")
    connection = storage.database.get_connection()
    events = EventStore(connection)
    trades = TradeRepository(connection)
    events.append(
        StoredEvent(
            session_id="s1",
            event_type="execution.settled",
            aggregate_id="t1",
            payload={"value": 1},
        )
    )

    result = ReplayEngine(events, trades).replay_session("s1")
    storage.close()

    assert result.reconstructed_state["execution_events"] == 1


def test_snapshot_and_recovery(tmp_path) -> None:
    storage = StorageSession.create(tmp_path / "test.db", session_id="s1")
    runtime_repo = RuntimeRepository(storage.database.get_connection())
    snapshot_manager = SnapshotManager(runtime_repo)
    state = RuntimeState(mode=RuntimeMode.PAPER)
    state.start()

    snapshot_manager.create_snapshot("s1", state, RiskEngine(), [])
    recovery = RecoveryManager(snapshot_manager).recover("s1")
    storage.close()

    assert recovery.recovered is True
    assert recovery.snapshot is not None


def test_persistence_service_persists_journal_and_events(tmp_path) -> None:
    service = PersistenceService(tmp_path / "test.db", session_id="s1")
    entry = TradeJournalEntry(
        trade_id=str(uuid4()),
        lifecycle_state="settled",
        strategy_name="sample",
        symbol="EURUSD",
        timeframe="1m",
        direction=SignalDirection.CALL.value,
        confidence=0.8,
        timestamp=utc_now(),
        pnl=0.8,
        outcome="win",
    )

    service.persist_trade_journal([entry])
    replay = ReplayEngine(service.events, service.trades).replay_trades("s1")
    service.close()

    assert replay["settled"] == 1
