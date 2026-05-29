"""Run read-only streaming diagnostics."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config.settings import Settings  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402
from app.streaming.candle_aggregator import CandleAggregator  # noqa: E402
from app.streaming.config import StreamingConfig  # noqa: E402
from app.streaming.csv_replay_stream import CsvReplayMarketStream  # noqa: E402
from app.streaming.models import MarketDataEvent, StreamEventType  # noqa: E402
from app.streaming.models import utc_now  # noqa: E402
from app.streaming.simulated_stream import SimulatedMarketStream  # noqa: E402
from app.streaming.stream_engine import StreamEngine  # noqa: E402
from app.streaming.validator import StreamValidator  # noqa: E402


def consume(engine: StreamEngine, limit: int, timeframe: str) -> list[MarketDataEvent]:
    """Consume a small deterministic event sample."""
    events = []
    for _ in range(limit):
        event, _validation = engine.poll(expected_timeframe=timeframe)
        if event is not None:
            events.append(event)
    return events


def main() -> None:
    """Initialize stream services, validate events, and print diagnostics."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)

    config = StreamingConfig.from_yaml(
        PROJECT_ROOT / "configs" / "streaming" / "simulated_stream.yaml"
    )
    simulated = SimulatedMarketStream(
        symbol=config.symbols[0],
        timeframes=tuple(config.timeframes),
        update_interval_seconds=config.update_interval_seconds,
        latency_ms=config.latency_ms,
        seed=config.seed,
        start_time=utc_now(),
    )
    validator = StreamValidator(
        stale_after_seconds=52560000,
        latency_warning_ms=5000,
        strict=config.validation_strict,
    )
    engine = StreamEngine(simulated, validator=validator)
    engine.start([("EURUSD", "1m")])
    simulated_events = consume(engine, 8, "1m")

    aggregator = CandleAggregator("1m", source="diagnostics")
    aggregation_sample = []
    for event in simulated_events:
        if event.event_type == StreamEventType.TICK and event.tick is not None:
            aggregation_sample.extend(aggregator.update(event.tick))
    simulated_health = simulated.get_health().to_dict()
    engine.stop()

    replay_config = StreamingConfig.from_yaml(
        PROJECT_ROOT / "configs" / "streaming" / "csv_replay_stream.yaml"
    )
    replay = CsvReplayMarketStream(
        PROJECT_ROOT / replay_config.csv_path,
        symbol=replay_config.symbols[0],
        timeframe=replay_config.timeframes[0],
        speed_multiplier=replay_config.speed_multiplier,
    )
    replay_engine = StreamEngine(
        replay,
        validator=StreamValidator(stale_after_seconds=52560000),
    )
    replay_engine.start([("EURUSD", "1m")])
    replay_events = consume(replay_engine, 5, "1m")
    replay_health = replay.get_health().to_dict()
    replay_engine.stop()

    no_execution_capability = not any(
        hasattr(stream, "place_trade") or hasattr(stream, "execute_trade")
        for stream in (simulated, replay)
    )

    diagnostics = {
        "simulated_events": len(simulated_events),
        "simulated_candles_buffered": len(engine.buffer.candles),
        "aggregation_sample": len(aggregation_sample),
        "simulated_health": simulated_health,
        "csv_replay_events": len(replay_events),
        "csv_replay_health": replay_health,
        "no_execution_capability": no_execution_capability,
    }
    print(diagnostics)


if __name__ == "__main__":
    main()
