"""Tests for Phase 12 external data integration research layer."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
import subprocess
import sys

from app.external_data.base_feed import ExternalFeedStreamAdapter, FeedContract
from app.external_data.comparison import FeedComparisonEngine
from app.external_data.feed_registry import ExternalFeedRegistry
from app.external_data.models import NormalizedCandle
from app.external_data.monitor import ExternalFeedMonitor
from app.external_data.normalizer import FeedNormalizer
from app.external_data.quality_analyzer import FeedQualityAnalyzer
from app.external_data.simulated_external_feed import SimulatedExternalFeed
from app.storage.persistence import PersistenceService
from app.streaming.stream_engine import StreamEngine
from app.streaming.validator import StreamValidator


def test_external_normalizer_standardizes_market_data() -> None:
    """Normalizer converts provider-like payloads into stable models."""
    normalizer = FeedNormalizer(price_precision=5)
    candle = normalizer.normalize_candle(
        {
            "symbol": "eur/usd",
            "timeframe": "M1",
            "timestamp": "2024-01-01T00:00:00Z",
            "open": "1.100001",
            "high": "1.101009",
            "low": "1.099991",
            "close": "1.100551",
        },
        source="test_source",
    )

    assert candle.symbol == "EURUSD"
    assert candle.timeframe == "1m"
    assert candle.timestamp.tzinfo is not None
    assert candle.close == 1.10055


def test_quality_analyzer_flags_duplicates_latency_stale_and_gaps() -> None:
    """Quality analyzer produces score and issue labels."""
    timestamp = datetime(2024, 1, 1, tzinfo=UTC)
    candles = [
        NormalizedCandle("EURUSD", "1m", timestamp, 1, 1.1, 0.9, 1.0, "a", latency_ms=1200),
        NormalizedCandle("EURUSD", "1m", timestamp, 1, 1.1, 0.9, 1.0, "a", latency_ms=1200),
        NormalizedCandle(
            "EURUSD",
            "1m",
            timestamp + timedelta(minutes=3),
            1,
            1.1,
            0.9,
            1.0,
            "a",
        ),
    ]
    analyzer = FeedQualityAnalyzer(
        stale_after_seconds=60,
        latency_warning_ms=1000,
        expected_interval_seconds=60,
    )

    metrics = analyzer.analyze(candles, now=timestamp + timedelta(minutes=5))

    assert metrics.duplicate_count == 1
    assert metrics.latency_warning_count == 2
    assert metrics.gap_count == 1
    assert metrics.quality_score < 100


def test_comparison_engine_compares_candles_latency_and_timestamps() -> None:
    """Comparison engine reports source differences."""
    timestamp = datetime(2024, 1, 1, tzinfo=UTC)
    left = [NormalizedCandle("EURUSD", "1m", timestamp, 1, 1.1, 0.9, 1.0, "a", latency_ms=10)]
    right = [
        NormalizedCandle(
            "EURUSD",
            "1m",
            timestamp + timedelta(seconds=1),
            1,
            1.2,
            0.9,
            1.0,
            "b",
            latency_ms=30,
        )
    ]

    report = FeedComparisonEngine(timestamp_tolerance_ms=100).compare(left, right)

    assert report.timestamp_mismatches == 1
    assert report.candle_mismatches == 1
    assert report.latency_delta_ms == 20


def test_simulated_external_feed_supports_quality_scenarios_and_read_only_contract() -> None:
    """Simulator can emit duplicates, gaps, reconnects, and exposes no execution methods."""
    feed = SimulatedExternalFeed(
        duplicate_every=2,
        missing_every=3,
        reconnect_every=4,
        seed=2,
    )
    feed.start()
    feed.subscribe("EURUSD", "1m")
    payloads = [feed.next_payload() for _ in range(6)]
    snapshot = feed.get_snapshot()
    feed.stop()

    assert len([payload for payload in payloads if payload is not None]) >= 4
    assert snapshot.reconnect_attempts >= 1
    assert not any(
        hasattr(feed, attr) for attr in ("place_trade", "execute_trade", "submit_order", "login")
    )


def test_external_feed_monitor_tracks_degradation() -> None:
    """Monitor records payload latency and quality degradation."""
    monitor = ExternalFeedMonitor(
        "test",
        analyzer=FeedQualityAnalyzer(latency_warning_ms=1),
        quality_threshold=99,
    )
    monitor.start()
    payload = NormalizedCandle(
        "EURUSD",
        "1m",
        datetime(2024, 1, 1, tzinfo=UTC),
        1,
        1.1,
        0.9,
        1.0,
        "test",
        latency_ms=10,
    )
    monitor.record_payload(payload)

    snapshot = monitor.snapshot(("EURUSD",), ("1m",))

    assert snapshot.status.value == "degraded"
    assert snapshot.latency.threshold_breached


def test_external_feed_stream_adapter_uses_existing_stream_engine() -> None:
    """External feed adapter routes normalized feed data through stream validation."""
    feed = SimulatedExternalFeed(seed=3)
    adapter = ExternalFeedStreamAdapter(feed)
    engine = StreamEngine(
        adapter,
        validator=StreamValidator(stale_after_seconds=52560000, latency_warning_ms=5000),
    )

    engine.start([("EURUSD", "1m")])
    event, validation = engine.poll(expected_timeframe="1m")
    engine.stop()

    assert event is not None
    assert validation is not None and validation.valid
    assert len(engine.buffer.events) == 1


def test_external_feed_registry_rejects_execution_capability() -> None:
    """Registry prevents forbidden execution-like feed surfaces."""

    class UnsafeFeed(SimulatedExternalFeed):
        def place_trade(self) -> None:
            return None

    registry = ExternalFeedRegistry()
    registry.register("unsafe", UnsafeFeed, FeedContract("unsafe"))

    try:
        registry.create("unsafe")
    except Exception as exc:
        assert "forbidden execution capability" in str(exc)
    else:
        raise AssertionError("unsafe feed registration should fail at creation")


def test_external_persistence_integration_records_reports(tmp_path) -> None:
    """External data reports persist through the existing event store."""
    service = PersistenceService(tmp_path / "external.db", session_id="external-test")

    service.persist_external_feed_snapshot("simulated", {"status": "running"})
    service.persist_external_quality_report("simulated", {"quality_score": 100})
    events = service.events.replay(event_type="external_data.feed_snapshot")
    service.close()

    assert len(events) == 1
    assert events[0].aggregate_id == "simulated"


def test_external_diagnostics_script_runs() -> None:
    """Diagnostics script initializes feed, validates quality, compares, and prints results."""
    result = subprocess.run(
        [sys.executable, "scripts/check_external_data.py"],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert "no_execution_capability" in result.stdout
    assert "quality" in result.stdout
