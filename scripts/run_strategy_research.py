"""Run the research CISD/FVG strategy candidate and export explainability reports."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loguru import logger  # noqa: E402

from app.analytics.strategy_research import (  # noqa: E402
    StrategyResearchAnalyzer,
    StrategyResearchExporter,
)
from app.backtesting.backtest_engine import BacktestEngine  # noqa: E402
from app.backtesting.simulator import BinaryOptionSimulator  # noqa: E402
from app.config.settings import Settings  # noqa: E402
from app.config.strategy_config import StrategyConfigLoader  # noqa: E402
from app.data.csv_loader import CsvCandleLoader  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402
from app.risk.risk_engine import RiskEngine  # noqa: E402
from app.storage.persistence import PersistenceService  # noqa: E402
from app.strategies.registry import default_strategy_registry  # noqa: E402


def main() -> None:
    """Load sample data, run research strategy, export analytics, and print summary."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)

    config = StrategyConfigLoader().load(
        PROJECT_ROOT / "configs" / "strategies" / "research_cisd_fvg_strategy.yaml"
    )
    strategy = default_strategy_registry().create_from_config(config)
    candles = CsvCandleLoader().load(
        PROJECT_ROOT / "data" / "sample_eurusd_m1.csv",
        symbol=config.symbols[0],
        timeframe=config.timeframes[0],
    )
    risk_engine = RiskEngine.from_profile(PROJECT_ROOT / "configs" / "risk" / "base_risk.yaml")
    engine = BacktestEngine(
        risk_engine=risk_engine,
        simulator=BinaryOptionSimulator(payout_percentage=0.80, expiry_candles=1, stake=1.0),
    )

    result = engine.run(strategy=strategy, candles=candles)
    decisions = list(getattr(strategy, "decisions", []))
    research_snapshot = StrategyResearchAnalyzer().analyze(decisions)
    report_paths = StrategyResearchExporter(PROJECT_ROOT / "reports" / "strategy_research").export(
        research_snapshot,
        decisions,
        "research_cisd_fvg",
    )

    persistence = PersistenceService(
        PROJECT_ROOT / "storage" / "trading_system.db",
        session_id="strategy_research",
    )
    persistence.persist_research_strategy_metadata(
        strategy.name,
        {
            "name": strategy.name,
            "version": strategy.metadata.version,
            "description": strategy.metadata.description,
            "parameters": config.parameters,
        },
    )
    for decision in decisions:
        persistence.persist_strategy_decision(strategy.name, decision.to_dict())
    persistence.persist_signal_evidence_summary(strategy.name, research_snapshot.to_dict())
    persistence.persist_trade_journal(engine.trade_journal.entries())
    persistence.persist_risk_events(risk_engine.events)
    persistence.close()

    confidences = [decision.confidence for decision in decisions if decision.generated_signal]
    average_confidence = round(sum(confidences) / len(confidences), 4) if confidences else 0.0
    summary = {
        "total_signals": research_snapshot.generated_signals,
        "executed_trades": result.metrics.get("total_trades", 0),
        "blocked_trades": result.metrics.get("blocked_trades", 0),
        "win_rate": result.metrics.get("win_rate", 0.0),
        "net_pnl": result.metrics.get("net_pnl", 0.0),
        "rejection_reasons": {
            **research_snapshot.rejection_reasons,
            **result.risk_summary.get("rejection_reason_counts", {}),
        },
        "average_confidence": average_confidence,
        "evidence_summary": research_snapshot.evidence_frequency,
        "reports": {key: str(path) for key, path in report_paths.items()},
    }
    logger.bind(component="strategy_research").info("Research run summary {}", summary)
    print(summary)


if __name__ == "__main__":
    main()
