"""Run a local paper trading runtime session."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loguru import logger  # noqa: E402

from app.analytics.dataset_builder import ResearchDatasetBuilder  # noqa: E402
from app.analytics.exporter import AnalyticsExporter  # noqa: E402
from app.analytics.performance_analyzer import PerformanceAnalyzer  # noqa: E402
from app.analytics.runtime_analytics import RuntimeAnalytics  # noqa: E402
from app.config.settings import Settings  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402
from app.runtime.metrics import RuntimeMetricsCalculator  # noqa: E402
from app.runtime.runtime_manager import RuntimeConfig, RuntimeManager  # noqa: E402
from app.strategies.sample_strategy import SampleCandleDirectionStrategy  # noqa: E402


def main() -> None:
    """Run a safe local paper trading session and print a summary."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)

    config_path = PROJECT_ROOT / "configs" / "runtime" / "paper_runtime.yaml"
    config = RuntimeConfig.from_yaml(config_path)
    strategy = SampleCandleDirectionStrategy()
    manager = RuntimeManager(config=config, strategy=strategy)
    state = manager.run()
    metrics = RuntimeMetricsCalculator().calculate(state)
    runtime_performance = RuntimeAnalytics().analyze(state)
    analytics_snapshot = PerformanceAnalyzer().analyze(
        manager.trade_journal.entries(),
        manager.equity_curve,
        runtime_performance=runtime_performance,
    )
    analytics_exporter = AnalyticsExporter(PROJECT_ROOT / "reports" / "analytics")
    analytics_exporter.export_snapshot(analytics_snapshot, "runtime_paper")
    analytics_exporter.export_journal(manager.trade_journal.entries(), "runtime_paper")
    analytics_exporter.export_equity_curve(manager.equity_curve.points(), "runtime_paper")
    ResearchDatasetBuilder().build_trade_dataset(
        manager.trade_journal.entries(),
        PROJECT_ROOT / "reports" / "analytics" / "runtime_paper_dataset.csv",
    )

    logger.info("Runtime state: {}", state.snapshot())
    logger.info("Runtime metrics: {}", metrics)
    logger.info("Runtime analytics: {}", analytics_snapshot.to_dict())
    logger.info("Paper balance: {}", manager.broker.get_balance())
    print(
        {
            "state": state.snapshot(),
            "metrics": metrics.__dict__,
            "balance": round(manager.broker.get_balance(), 4),
            "trade_history_events": len(manager.broker.get_trade_history()),
        }
    )


if __name__ == "__main__":
    main()
