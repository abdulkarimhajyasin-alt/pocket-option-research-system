"""Run read-only external data diagnostics."""

from pathlib import Path
import sys

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.analytics.external_data_analytics import ExternalDataAnalytics  # noqa: E402
from app.config.settings import Settings  # noqa: E402
from app.external_data.base_feed import ExternalFeedStreamAdapter, FeedContract  # noqa: E402
from app.external_data.comparison import FeedComparisonEngine  # noqa: E402
from app.external_data.feed_registry import ExternalFeedRegistry  # noqa: E402
from app.external_data.models import utc_now  # noqa: E402
from app.external_data.quality_analyzer import FeedQualityAnalyzer  # noqa: E402
from app.external_data.simulated_external_feed import SimulatedExternalFeed  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402
from app.storage.persistence import PersistenceService  # noqa: E402
from app.streaming.stream_engine import StreamEngine  # noqa: E402
from app.streaming.validator import StreamValidator  # noqa: E402


def _load_yaml(path: Path) -> dict[str, object]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _build_feed(config: dict[str, object], source_suffix: str = "") -> SimulatedExternalFeed:
    source = str(config.get("source", "simulated_external")) + source_suffix
    return SimulatedExternalFeed(
        source=source,
        symbol=str(config.get("symbol", "EURUSD")),
        timeframe=str(config.get("timeframe", "1m")),
        latency_ms=float(config.get("latency_ms", 75)),
        seed=int(config.get("seed", 12)),
        start_time=utc_now(),
        missing_every=int(config.get("missing_every", 0)),
        duplicate_every=int(config.get("duplicate_every", 0)),
        stale_every=int(config.get("stale_every", 0)),
        reconnect_every=int(config.get("reconnect_every", 0)),
    )


def _collect(feed: SimulatedExternalFeed, count: int) -> list[object]:
    feed.start()
    feed.subscribe(feed.symbol, feed.timeframe)
    payloads = [feed.next_payload() for _ in range(count)]
    feed.stop()
    return [payload for payload in payloads if payload is not None]


def main() -> None:
    """Initialize feed, validate quality, compare samples, persist diagnostics, and print results."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)

    feed_config = _load_yaml(PROJECT_ROOT / "configs" / "external_data" / "simulated_feed.yaml")
    quality_config = _load_yaml(PROJECT_ROOT / "configs" / "external_data" / "feed_quality.yaml")

    registry = ExternalFeedRegistry()
    registry.register(
        "simulated",
        lambda: _build_feed(feed_config),
        FeedContract("simulated"),
    )
    feed = registry.create("simulated")
    assert isinstance(feed, SimulatedExternalFeed)

    payloads = _collect(feed, 8)
    analyzer = FeedQualityAnalyzer(
        stale_after_seconds=float(quality_config.get("stale_after_seconds", 120)),
        latency_warning_ms=float(quality_config.get("latency_warning_ms", 1000)),
        expected_interval_seconds=float(quality_config.get("expected_interval_seconds", 60)),
    )
    quality = analyzer.analyze(payloads)
    latency = analyzer.latency_metrics(payloads)
    snapshot = feed.get_snapshot()
    analytics = ExternalDataAnalytics().analyze(snapshot)

    comparison_feed = _build_feed(feed_config, source_suffix="_comparison")
    comparison_payloads = _collect(comparison_feed, 8)
    comparison = FeedComparisonEngine(
        timestamp_tolerance_ms=float(
            (quality_config.get("comparison") or {}).get("timestamp_tolerance_ms", 250)
        ),
        price_tolerance=float(
            (quality_config.get("comparison") or {}).get("price_tolerance", 0.0001)
        ),
    ).compare(payloads, comparison_payloads)

    adapter_feed = _build_feed(feed_config, source_suffix="_adapter")
    adapter = ExternalFeedStreamAdapter(adapter_feed)
    engine = StreamEngine(
        adapter,
        validator=StreamValidator(stale_after_seconds=52560000, latency_warning_ms=5000),
    )
    engine.start([(adapter_feed.symbol, adapter_feed.timeframe)])
    stream_event, validation = engine.poll(expected_timeframe=adapter_feed.timeframe)
    engine.stop()

    persistence = PersistenceService(PROJECT_ROOT / "storage" / "external_data_diagnostics.db")
    persistence.persist_external_feed_snapshot(feed.source, snapshot.to_dict())
    persistence.persist_external_quality_report(feed.source, quality.to_dict())
    persistence.persist_external_latency_metrics(feed.source, latency.to_dict())
    if quality.issues:
        persistence.persist_external_feed_incident(feed.source, quality.to_dict())
    persistence.close()

    forbidden_attrs = ("place_trade", "execute_trade", "submit_order", "login")
    diagnostics = {
        "registered_feeds": registry.names(),
        "payloads": len(payloads),
        "quality": quality.to_dict(),
        "latency": latency.to_dict(),
        "snapshot": snapshot.to_dict(),
        "analytics": analytics.to_dict(),
        "comparison": comparison.to_dict(),
        "stream_adapter_event": stream_event.to_dict() if stream_event else None,
        "stream_validation": validation.to_dict() if validation else None,
        "no_execution_capability": not any(hasattr(feed, attr) for attr in forbidden_attrs),
    }
    print(diagnostics)


if __name__ == "__main__":
    main()
