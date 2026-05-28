"""Tests for analytics and research infrastructure."""

from datetime import UTC, datetime

from app.analytics.dataset_builder import ResearchDatasetBuilder
from app.analytics.equity_curve import EquityCurveTracker
from app.analytics.exporter import AnalyticsExporter
from app.analytics.models import TradeJournalEntry
from app.analytics.performance_analyzer import PerformanceAnalyzer
from app.analytics.session_analytics import SessionAnalytics
from app.analytics.symbol_analytics import SymbolAnalytics
from app.analytics.trade_journal import TradeJournal


def _entry(
    trade_id: str,
    state: str,
    hour: int,
    outcome: str | None = None,
    pnl: float = 0.0,
    symbol: str = "EURUSD",
    reason: str | None = None,
) -> TradeJournalEntry:
    return TradeJournalEntry(
        trade_id=trade_id,
        lifecycle_state=state,
        strategy_name="sample",
        symbol=symbol,
        timeframe="1m",
        direction="call",
        confidence=0.75,
        timestamp=datetime(2026, 1, 1, hour, 0, tzinfo=UTC),
        pnl=pnl,
        outcome=outcome,
        rejection_reason=reason,
    )


def test_trade_journal_records_searches_and_exports(tmp_path) -> None:
    journal = TradeJournal()
    journal.append(_entry("1", "executed", 8))
    journal.append(_entry("1", "settled", 8, outcome="win", pnl=0.8))

    assert len(journal.entries()) == 2
    assert len(journal.search(lifecycle_state="settled")) == 1
    assert journal.export_json(tmp_path / "journal.json").exists()
    assert journal.export_csv(tmp_path / "journal.csv").exists()


def test_equity_curve_tracks_drawdown_and_cumulative_pnl() -> None:
    tracker = EquityCurveTracker(initial_equity=100.0)
    tracker.update(datetime(2026, 1, 1, tzinfo=UTC), 110.0, pnl=10.0)
    tracker.update(datetime(2026, 1, 2, tzinfo=UTC), 105.0, pnl=-5.0)

    points = tracker.points()
    assert points[-1].cumulative_pnl == 5.0
    assert tracker.max_drawdown == 5.0


def test_session_and_symbol_analytics() -> None:
    entries = [
        _entry("1", "settled", 8, outcome="win", pnl=0.8, symbol="EURUSD"),
        _entry("2", "blocked", 13, symbol="GBPUSD", reason="minimum_confidence"),
    ]

    sessions = SessionAnalytics().analyze(entries)
    symbols = SymbolAnalytics().analyze(entries)

    assert any(session.session_name == "london" and session.trades == 1 for session in sessions)
    assert {symbol.symbol for symbol in symbols} == {"EURUSD", "GBPUSD"}
    assert next(symbol for symbol in symbols if symbol.symbol == "GBPUSD").rejection_count == 1


def test_performance_snapshot_and_exports(tmp_path) -> None:
    entries = [
        _entry("1", "executed", 8),
        _entry("1", "settled", 8, outcome="win", pnl=0.8),
        _entry("2", "blocked", 9, reason="minimum_confidence"),
    ]
    equity = EquityCurveTracker(initial_equity=100.0)
    equity.update(datetime(2026, 1, 1, 8, 0, tzinfo=UTC), 100.8, pnl=0.8)
    snapshot = PerformanceAnalyzer().analyze(entries, equity)

    exporter = AnalyticsExporter(tmp_path)
    assert snapshot.trade_count == 1
    assert snapshot.rejection_analysis["minimum_confidence"] == 1
    assert exporter.export_snapshot(snapshot, "sample")["json"].exists()
    assert exporter.export_journal(entries, "sample")["csv"].exists()
    assert exporter.export_equity_curve(equity.points(), "sample")["csv"].exists()


def test_dataset_builder_exports_normalized_csv(tmp_path) -> None:
    dataset_path = ResearchDatasetBuilder().build_trade_dataset(
        [_entry("1", "settled", 8, outcome="loss", pnl=-1.0)],
        tmp_path / "dataset.csv",
    )

    content = dataset_path.read_text(encoding="utf-8")
    assert "is_loss" in content
    assert "sample" in content
