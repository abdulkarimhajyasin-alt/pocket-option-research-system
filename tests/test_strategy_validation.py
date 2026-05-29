"""Tests for strategy validation and research quality tooling."""

from __future__ import annotations

import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.analytics.validation_quality import ValidationQualityAnalyzer
from app.config.strategy_config import StrategyConfig
from app.data.models import Candle, CandleSeries
from app.storage.persistence import PersistenceService
from app.validation.comparison import ResearchComparisonEngine, ResearchComparisonItem
from app.validation.dataset import DatasetManager
from app.validation.models import (
    DatasetDescriptor,
    RobustnessCategory,
    ValidationMetrics,
    ValidationRunResult,
    WarningSeverity,
    WindowMode,
)
from app.validation.out_of_sample import OutOfSampleConfig, OutOfSampleValidator
from app.validation.overfitting import OverfittingDetector
from app.validation.parameter_sweep import ParameterSweepConfig, ParameterSweepEngine
from app.validation.reporting import ResearchReportBuilder, ResearchReportExporter
from app.validation.robustness import RobustnessScorer
from app.validation.walk_forward import WalkForwardConfig, WalkForwardValidator


class FakeRunner:
    """Small deterministic validation runner for unit tests."""

    def run(
        self,
        strategy_config: StrategyConfig,
        candles: CandleSeries,
        dataset: DatasetDescriptor,
        period_label: str,
        parameter_overrides: dict[str, object] | None = None,
    ) -> ValidationRunResult:
        """Return metrics based on sample size and parameters."""
        overrides = parameter_overrides or {}
        confidence_threshold = float(overrides.get("confidence_threshold", 0.6))
        signal_count = max(0, len(candles) // 8 - int(confidence_threshold * 2))
        net_pnl = round(signal_count * (0.35 + confidence_threshold / 10.0), 4)
        metrics = ValidationMetrics(
            signal_count=signal_count,
            executed_trades=max(0, signal_count - 1),
            blocked_trades=1 if signal_count else 0,
            win_rate=round(0.45 + min(0.2, signal_count / 200.0), 4),
            net_pnl=net_pnl,
            max_drawdown=round(max(0.0, signal_count / 20.0), 4),
            rejection_rate=0.05,
            average_confidence=confidence_threshold,
            profit_factor=1.2,
        )
        return ValidationRunResult(
            run_id=period_label,
            strategy_name=strategy_config.name,
            dataset=dataset,
            parameters={**strategy_config.parameters, **overrides},
            metrics=metrics,
            period_label=period_label,
            start=candles.first.timestamp if candles.first else None,
            end=candles.last.timestamp if candles.last else None,
        )


def make_candles(count: int = 240) -> CandleSeries:
    """Build deterministic candles."""
    base = datetime(2026, 1, 1, tzinfo=UTC)
    candles = []
    price = 1.1000
    for index in range(count):
        open_price = price
        close = price + (0.0002 if index % 2 == 0 else -0.0001)
        high = max(open_price, close) + 0.0002
        low = min(open_price, close) - 0.0002
        candles.append(
            Candle(
                symbol="EURUSD",
                timeframe="1m",
                timestamp=base + timedelta(minutes=index),
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=100.0,
            )
        )
        price = close
    return CandleSeries("EURUSD", "1m", candles)


def make_strategy_config() -> StrategyConfig:
    """Build a minimal strategy config."""
    return StrategyConfig(
        name="research_cisd_fvg_strategy",
        symbols=["EURUSD"],
        timeframes=["1m"],
        parameters={"minimum_history": 20},
        confidence_threshold=0.58,
    )


def make_components() -> tuple[StrategyConfig, CandleSeries, DatasetManager, FakeRunner]:
    """Build shared validation fixtures."""
    return make_strategy_config(), make_candles(), DatasetManager(), FakeRunner()


def test_dataset_descriptor_and_slice() -> None:
    candles = make_candles(10)
    manager = DatasetManager()
    descriptor = manager.describe(candles, "unit", "memory.csv")
    sliced = manager.slice(candles, 2, 5)
    assert descriptor.sample_count == 10
    assert descriptor.symbol == "EURUSD"
    assert len(sliced) == 3
    assert sliced.first.timestamp == candles[2].timestamp


def test_walk_forward_validation() -> None:
    strategy_config, candles, manager, runner = make_components()
    config = WalkForwardConfig(
        mode=WindowMode.ROLLING,
        train_size=80,
        validation_size=40,
        test_size=40,
        step_size=40,
        minimum_samples=120,
    )
    result = WalkForwardValidator(runner, manager).run(
        strategy_config,
        candles,
        "unit",
        "memory.csv",
        config,
    )
    assert len(result.windows) == 3
    assert result.aggregate_metrics["windows"] == 3
    assert "pnl_variation" in result.stability_metrics


def test_out_of_sample_validation() -> None:
    strategy_config, candles, manager, runner = make_components()
    result = OutOfSampleValidator(runner, manager).run(
        strategy_config,
        candles,
        "unit",
        "memory.csv",
        OutOfSampleConfig(in_sample_ratio=0.6, minimum_samples=100),
    )
    assert result.in_sample.period_label == "in_sample"
    assert result.out_of_sample.period_label == "out_of_sample"
    assert result.stability_score >= 0
    assert "win_rate_degradation" in result.degradation_metrics


def test_parameter_sweep_validation() -> None:
    strategy_config, candles, manager, runner = make_components()
    config = ParameterSweepConfig(
        grid={"confidence_threshold": [0.56, 0.58], "minimum_body_ratio": [0.3, 0.4]},
        max_combinations=4,
    )
    summary = ParameterSweepEngine(runner, manager).run(
        strategy_config,
        candles,
        "unit",
        "memory.csv",
        config,
    )
    assert len(summary.results) == 4
    assert summary.best_parameter_sets
    assert summary.worst_parameter_sets


def test_robustness_and_overfitting_detection() -> None:
    strategy_config, candles, manager, runner = make_components()
    wf = WalkForwardValidator(runner, manager).run(
        strategy_config,
        candles,
        "unit",
        "memory.csv",
        WalkForwardConfig(train_size=80, validation_size=40, test_size=40, step_size=40),
    )
    oos = OutOfSampleValidator(runner, manager).run(
        strategy_config,
        candles,
        "unit",
        "memory.csv",
        OutOfSampleConfig(in_sample_ratio=0.6),
    )
    sweep = ParameterSweepEngine(runner, manager).run(
        strategy_config,
        candles,
        "unit",
        "memory.csv",
        ParameterSweepConfig(grid={"confidence_threshold": [0.5, 0.9]}),
    )
    robustness = RobustnessScorer().score(wf, oos, sweep)
    warnings = OverfittingDetector().detect(wf, oos, sweep)
    assert robustness.category in set(RobustnessCategory)
    assert 0 <= robustness.score <= 100
    assert all(warning.severity in set(WarningSeverity) for warning in warnings)


def test_comparison_engine() -> None:
    strategy_config, candles, manager, runner = make_components()
    descriptor = manager.describe(candles, "unit", "memory.csv")
    run = runner.run(strategy_config, candles, descriptor, "comparison")
    robustness = RobustnessScorer().score()
    comparison = ResearchComparisonEngine().compare(
        [ResearchComparisonItem("candidate", run, robustness)]
    )
    assert comparison["rankings"][0]["name"] == "candidate"


def test_report_generation_and_analytics(tmp_path: Path) -> None:
    strategy_config, candles, manager, runner = make_components()
    descriptor = manager.describe(candles, "unit", "memory.csv")
    run = runner.run(strategy_config, candles, descriptor, "report")
    robustness = RobustnessScorer().score()
    report = ResearchReportBuilder().build(
        strategy_config.name,
        descriptor,
        run.parameters,
        robustness,
        [],
    )
    paths = ResearchReportExporter(tmp_path).export(report, "unit")
    analytics = ValidationQualityAnalyzer().analyze(report)
    assert paths["json"].exists()
    assert paths["csv"].exists()
    assert paths["text"].read_text(encoding="utf-8").startswith("Strategy Validation")
    assert analytics.dataset_sample_count == len(candles)


def test_persistence_integration(tmp_path: Path) -> None:
    persistence = PersistenceService(tmp_path / "validation.db", session_id="unit_validation")
    payload: dict[str, Any] = {"score": 72.5}
    persistence.persist_validation_run("strategy", payload)
    events = persistence.events.replay(
        session_id="unit_validation",
        event_type="strategy_validation.run",
    )
    persistence.close()
    assert len(events) == 1
    assert events[0].payload == payload


def test_cli_walk_forward_smoke() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/run_walk_forward.py"],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert "windows" in completed.stdout
