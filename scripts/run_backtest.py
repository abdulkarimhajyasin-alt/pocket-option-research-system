"""Run a sample backtest through the Phase 2 foundation."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loguru import logger  # noqa: E402

from app.analytics.dataset_builder import ResearchDatasetBuilder  # noqa: E402
from app.analytics.exporter import AnalyticsExporter  # noqa: E402
from app.backtesting.backtest_engine import BacktestEngine  # noqa: E402
from app.backtesting.report_builder import BacktestReportBuilder  # noqa: E402
from app.backtesting.simulator import BinaryOptionSimulator  # noqa: E402
from app.config.settings import Settings  # noqa: E402
from app.data.csv_loader import CsvCandleLoader  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402
from app.risk.risk_engine import RiskEngine  # noqa: E402
from app.storage.persistence import PersistenceService  # noqa: E402
from app.strategies.sample_strategy import SampleCandleDirectionStrategy  # noqa: E402


def main() -> None:
    """Load sample data, run a backtest, and export reports."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)

    data_path = PROJECT_ROOT / "data" / "sample_eurusd_m1.csv"
    loader = CsvCandleLoader()
    candles = loader.load(data_path, symbol="EURUSD", timeframe="1m")

    strategy = SampleCandleDirectionStrategy()
    risk_profile = PROJECT_ROOT / "configs" / "risk" / "base_risk.yaml"
    risk_engine = RiskEngine.from_profile(risk_profile)
    simulator = BinaryOptionSimulator(payout_percentage=0.80, expiry_candles=1, stake=1.0)
    engine = BacktestEngine(risk_engine=risk_engine, simulator=simulator)

    result = engine.run(strategy=strategy, candles=candles)
    persistence = PersistenceService(
        PROJECT_ROOT / "storage" / "trading_system.db",
        session_id="sample_backtest",
    )
    persistence.persist_trade_journal(engine.trade_journal.entries())
    persistence.persist_risk_events(risk_engine.events)
    report_paths = BacktestReportBuilder(PROJECT_ROOT / "reports").export(
        result,
        run_name="sample_eurusd_m1",
    )
    snapshot = engine.performance_analyzer.analyze(
        engine.trade_journal.entries(),
        engine.equity_tracker,
    )
    persistence.persist_analytics_snapshot(snapshot, "backtest")
    analytics_exporter = AnalyticsExporter(PROJECT_ROOT / "reports" / "analytics")
    analytics_exporter.export_snapshot(snapshot, "sample_eurusd_m1")
    analytics_exporter.export_journal(engine.trade_journal.entries(), "sample_eurusd_m1")
    analytics_exporter.export_equity_curve(engine.equity_tracker.points(), "sample_eurusd_m1")
    ResearchDatasetBuilder().build_trade_dataset(
        engine.trade_journal.entries(),
        PROJECT_ROOT / "reports" / "analytics" / "sample_eurusd_m1_dataset.csv",
    )

    logger.info("Backtest metrics: {}", result.metrics)
    logger.info("Report files: {}", report_paths)
    persistence.close()
    print(result.summary())


if __name__ == "__main__":
    main()
