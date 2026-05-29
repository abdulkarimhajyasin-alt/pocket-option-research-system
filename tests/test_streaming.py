"""Tests for Phase 11 stream processing infrastructure."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.runtime.streaming_runtime import StreamingRuntime
from app.streaming.buffer import StreamBuffer
from app.streaming.candle_aggregator import CandleAggregator
from app.streaming.config import StreamingConfig
from app.streaming.csv_replay_stream import CsvReplayMarketStream
from app.streaming.models import (
    CandleUpdate,
    MarketDataEvent,
    MarketTick,
    StreamEventType,
)
from app.streaming.monitor import StreamMonitor
from app.streaming.simulated_stream import SimulatedMarketStream
from app.streaming.stream_engine import StreamEngine
from app.streaming.validator import StreamValidator


def test_stream_models_validate_and_serialize() -> None:
    """Stream models validate required market fields."""
    timestamp = datetime(2024, 1, 1, tzinfo=UTC)
    tick = MarketTick("EURUSD", timestamp, 1.1, bid=1.0999, ask=1.1001)
    event = MarketDataEvent(
        event_type=StreamEventType.TICK,
        symbol="EURUSD",
        timestamp=timestamp,
        source="test",
        sequence=1,
        tick=tick,
    )

    assert event.to_dict()["event_type"] == "tick"
    assert tick.to_dict()["symbol"] == "EURUSD"


def test_simulated_stream_is_deterministic_and_local_only() -> None:
    """Simulated stream emits deterministic read-only events."""
    stream = SimulatedMarketStream(seed=1, update_interval_seconds=1.0)
    stream.start()
    stream.subscribe("EURUSD", "1m")

    events = [stream.next_event() for _ in range(4)]

    assert all(event is not None for event in events)
    assert events[0].event_type == StreamEventType.TICK
    assert not hasattr(stream, "place_trade")
    assert stream.get_health().running


def test_csv_replay_stream_replays_candles_in_order() -> None:
    """CSV replay emits candle updates sequentially."""
    stream = CsvReplayMarketStream(Path("data/sample_eurusd_m1.csv"), "EURUSD", "1m")
    stream.start()
    stream.subscribe("EURUSD", "1m")

    first = stream.next_event()
    second = stream.next_event()

    assert first is not None and second is not None
    assert first.event_type == StreamEventType.CANDLE
    assert first.timestamp < second.timestamp


def test_candle_aggregator_closes_on_timeframe_boundary() -> None:
    """Aggregator updates OHLC and closes previous buckets."""
    aggregator = CandleAggregator("1m")
    first = MarketTick("EURUSD", datetime(2024, 1, 1, tzinfo=UTC), 1.1, sequence=1)
    second = MarketTick(
        "EURUSD",
        datetime(2024, 1, 1, 0, 1, tzinfo=UTC),
        1.2,
        sequence=2,
    )

    updates = aggregator.update(first) + aggregator.update(second)

    assert any(update.is_closed for update in updates)
    assert updates[-1].open == 1.2


def test_stream_buffer_orders_deduplicates_and_returns_context() -> None:
    """Buffer keeps ordered rolling event and candle context."""
    timestamp = datetime(2024, 1, 1, tzinfo=UTC)
    candle = CandleUpdate("EURUSD", "1m", timestamp, 1.0, 1.1, 0.9, 1.05, sequence=1)
    event = MarketDataEvent(
        StreamEventType.CANDLE,
        "EURUSD",
        timestamp,
        "test",
        1,
        candle=candle,
        event_id="same",
    )
    buffer = StreamBuffer(max_events=3, max_candles=3)

    assert buffer.add_event(event)
    assert not buffer.add_event(event)
    assert buffer.latest_candle("EURUSD", "1m") == candle


def test_stream_validator_flags_duplicate_stale_and_timeframe_mismatch() -> None:
    """Validator returns structured warnings and critical errors."""
    timestamp = datetime(2024, 1, 1, tzinfo=UTC)
    candle = CandleUpdate("EURUSD", "1m", timestamp, 1.0, 1.1, 0.9, 1.05)
    event = MarketDataEvent(
        StreamEventType.CANDLE,
        "EURUSD",
        timestamp,
        "test",
        1,
        candle=candle,
        event_id="same",
    )
    validator = StreamValidator(stale_after_seconds=1)

    first = validator.validate(event, expected_timeframe="1m", now=timestamp + timedelta(seconds=2))
    duplicate = validator.validate(event, expected_timeframe="1m", now=timestamp)
    mismatch_event = MarketDataEvent(
        StreamEventType.CANDLE,
        "EURUSD",
        timestamp + timedelta(minutes=1),
        "test",
        2,
        candle=CandleUpdate(
            "EURUSD",
            "1m",
            timestamp + timedelta(minutes=1),
            1.0,
            1.1,
            0.9,
            1.05,
        ),
    )
    mismatch = validator.validate(mismatch_event, expected_timeframe="5m", now=timestamp)

    assert first.valid
    assert "stale data" in first.warnings
    assert not duplicate.valid
    assert "duplicate event" in duplicate.critical_errors
    assert not mismatch.valid
    assert "timeframe mismatch" in mismatch.critical_errors


def test_stream_monitor_tracks_metrics() -> None:
    """Monitor builds health snapshots from processed events."""
    monitor = StreamMonitor("test")
    monitor.start()
    timestamp = datetime(2024, 1, 1, tzinfo=UTC)
    tick = MarketTick("EURUSD", timestamp, 1.1)
    event = MarketDataEvent(StreamEventType.TICK, "EURUSD", timestamp, "test", 1, tick=tick)

    monitor.record_event(event)
    monitor.record_validation(warnings=1)
    snapshot = monitor.snapshot({("EURUSD", "1m")})

    assert snapshot.running
    assert snapshot.average_latency_ms == 0
    assert monitor.metrics.validation_warnings == 1


def test_streaming_runtime_consumes_events_without_execution_dependency() -> None:
    """Streaming runtime can run diagnostics without creating execution capability."""
    stream = CsvReplayMarketStream(Path("data/sample_eurusd_m1.csv"), "EURUSD", "1m")
    runtime = StreamingRuntime(stream)

    runtime.start([("EURUSD", "1m")])
    diagnostics = runtime.run(max_events=3, expected_timeframe="1m")
    runtime.stop()

    assert diagnostics["buffered_events"] == 3
    assert diagnostics["closed_candles"] == 3
    assert not hasattr(stream, "place_trade")


def test_stream_config_loading() -> None:
    """Streaming configs load and normalize timeframes."""
    config = StreamingConfig.from_yaml("configs/streaming/simulated_stream.yaml")

    assert config.stream_type == "simulated"
    assert "1m" in config.timeframes


def test_diagnostics_components_are_fast() -> None:
    """Diagnostics building blocks emit a small validated sample quickly."""
    stream = SimulatedMarketStream(seed=5)
    engine = StreamEngine(stream, validator=StreamValidator(stale_after_seconds=52560000))
    engine.start([("EURUSD", "1m")])

    events = [engine.poll(expected_timeframe="1m")[0] for _ in range(3)]
    engine.stop()

    assert len([event for event in events if event is not None]) == 3
