"""Reusable validation backtest runner."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from uuid import uuid4

from app.backtesting.backtest_engine import BacktestEngine
from app.backtesting.simulator import BinaryOptionSimulator
from app.config.strategy_config import StrategyConfig
from app.data.models import CandleSeries
from app.risk.risk_engine import RiskEngine
from app.strategies.registry import default_strategy_registry
from app.validation.dataset import DatasetManager
from app.validation.models import DatasetDescriptor, ValidationMetrics, ValidationRunResult


class ValidationBacktestRunner:
    """Runs isolated strategy validations without broker dependencies."""

    def __init__(
        self,
        risk_profile_path: Path | str,
        simulator: BinaryOptionSimulator | None = None,
    ) -> None:
        self.risk_profile_path = Path(risk_profile_path)
        self.simulator = simulator or BinaryOptionSimulator(
            payout_percentage=0.80,
            expiry_candles=1,
            stake=1.0,
        )
        self.dataset_manager = DatasetManager()

    def run(
        self,
        strategy_config: StrategyConfig,
        candles: CandleSeries,
        dataset: DatasetDescriptor,
        period_label: str,
        parameter_overrides: dict[str, object] | None = None,
    ) -> ValidationRunResult:
        """Run one deterministic validation sample."""
        config = self._with_overrides(strategy_config, parameter_overrides or {})
        strategy = default_strategy_registry().create_from_config(config)
        risk_engine = RiskEngine.from_profile(self.risk_profile_path)
        engine = BacktestEngine(risk_engine=risk_engine, simulator=self.simulator)
        result = engine.run(strategy=strategy, candles=candles)
        decisions = list(getattr(strategy, "decisions", []))
        signal_decisions = [decision for decision in decisions if decision.generated_signal]
        confidences = [decision.confidence for decision in signal_decisions]
        if not confidences:
            confidences = [trade.confidence for trade in result.trades]
        average_confidence = round(sum(confidences) / len(confidences), 4) if confidences else 0.0
        signal_count = len(signal_decisions) if decisions else len(result.trades)
        metrics = ValidationMetrics.from_backtest(
            result.metrics,
            signal_count=signal_count,
            average_confidence=average_confidence,
        )
        return ValidationRunResult(
            run_id=str(uuid4()),
            strategy_name=strategy.name,
            dataset=dataset,
            parameters=config.parameters,
            metrics=metrics,
            period_label=period_label,
            start=candles.first.timestamp if candles.first else None,
            end=candles.last.timestamp if candles.last else None,
        )

    def _with_overrides(
        self,
        config: StrategyConfig,
        overrides: dict[str, object],
    ) -> StrategyConfig:
        parameters = deepcopy(config.parameters)
        parameters.update(overrides)
        updated = StrategyConfig(
            name=config.name,
            enabled=config.enabled,
            parameters=parameters,
            confidence_threshold=float(
                overrides.get("confidence_threshold", config.confidence_threshold)
            ),
            session_filters=list(config.session_filters),
            symbols=list(config.symbols),
            timeframes=list(config.timeframes),
        )
        updated.validate()
        return updated
