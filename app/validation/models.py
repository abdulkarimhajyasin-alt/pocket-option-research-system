"""Research validation domain models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class WindowMode(StrEnum):
    """Supported walk-forward split modes."""

    ROLLING = "rolling"
    EXPANDING = "expanding"


class RobustnessCategory(StrEnum):
    """Human-readable robustness categories."""

    VERY_WEAK = "Very Weak"
    WEAK = "Weak"
    MODERATE = "Moderate"
    STRONG = "Strong"
    RESEARCH_GRADE = "Research Grade"


class WarningSeverity(StrEnum):
    """Overfitting warning severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class DatasetDescriptor:
    """Identifies exactly which data was used for a validation run."""

    name: str
    source: str
    symbol: str
    timeframe: str
    start: datetime | None
    end: datetime | None
    sample_count: int
    validation_splits: dict[str, Any] = field(default_factory=dict)
    dataset_id: str | None = None
    version: str | None = None
    checksum: str | None = None
    quality_score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable descriptor."""
        payload = asdict(self)
        payload["start"] = self.start.isoformat() if self.start else None
        payload["end"] = self.end.isoformat() if self.end else None
        return payload


@dataclass(frozen=True)
class ValidationMetrics:
    """Compact, comparable validation metrics."""

    signal_count: int = 0
    executed_trades: int = 0
    blocked_trades: int = 0
    win_rate: float = 0.0
    net_pnl: float = 0.0
    max_drawdown: float = 0.0
    rejection_rate: float = 0.0
    average_confidence: float = 0.0
    profit_factor: float = 0.0

    @classmethod
    def from_backtest(
        cls,
        metrics: dict[str, float | int],
        signal_count: int,
        average_confidence: float,
    ) -> "ValidationMetrics":
        """Build metrics from a backtest result plus research decision summaries."""
        return cls(
            signal_count=signal_count,
            executed_trades=int(metrics.get("total_trades", 0)),
            blocked_trades=int(metrics.get("blocked_trades", 0)),
            win_rate=float(metrics.get("win_rate", 0.0)),
            net_pnl=float(metrics.get("net_pnl", 0.0)),
            max_drawdown=float(metrics.get("max_drawdown", 0.0)),
            rejection_rate=float(metrics.get("rejection_rate", 0.0)),
            average_confidence=average_confidence,
            profit_factor=float(metrics.get("profit_factor", 0.0)),
        )

    def to_dict(self) -> dict[str, float | int]:
        """Return metrics as a serializable dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class ValidationRunResult:
    """One isolated strategy validation run."""

    run_id: str
    strategy_name: str
    dataset: DatasetDescriptor
    parameters: dict[str, Any]
    metrics: ValidationMetrics
    period_label: str
    start: datetime | None
    end: datetime | None

    def to_dict(self) -> dict[str, Any]:
        """Return serializable run output."""
        return {
            "run_id": self.run_id,
            "strategy_name": self.strategy_name,
            "dataset": self.dataset.to_dict(),
            "parameters": self.parameters,
            "metrics": self.metrics.to_dict(),
            "period_label": self.period_label,
            "start": self.start.isoformat() if self.start else None,
            "end": self.end.isoformat() if self.end else None,
        }


@dataclass(frozen=True)
class WalkForwardWindow:
    """One train/validation/test split."""

    index: int
    train_start: int
    train_end: int
    validation_start: int
    validation_end: int
    test_start: int
    test_end: int

    def to_dict(self) -> dict[str, int]:
        """Return window boundaries."""
        return asdict(self)


@dataclass(frozen=True)
class WalkForwardWindowResult:
    """Validation result for one walk-forward window."""

    window: WalkForwardWindow
    train: ValidationRunResult
    validation: ValidationRunResult
    test: ValidationRunResult

    def to_dict(self) -> dict[str, Any]:
        """Return serializable window result."""
        return {
            "window": self.window.to_dict(),
            "train": self.train.to_dict(),
            "validation": self.validation.to_dict(),
            "test": self.test.to_dict(),
        }


@dataclass(frozen=True)
class WalkForwardResult:
    """Aggregate walk-forward validation output."""

    strategy_name: str
    mode: WindowMode
    windows: list[WalkForwardWindowResult]
    aggregate_metrics: dict[str, float | int]
    stability_metrics: dict[str, float | int]

    def to_dict(self) -> dict[str, Any]:
        """Return serializable walk-forward output."""
        return {
            "strategy_name": self.strategy_name,
            "mode": self.mode.value,
            "windows": [window.to_dict() for window in self.windows],
            "aggregate_metrics": self.aggregate_metrics,
            "stability_metrics": self.stability_metrics,
        }


@dataclass(frozen=True)
class OutOfSampleResult:
    """Separated in-sample/out-of-sample evaluation."""

    strategy_name: str
    in_sample: ValidationRunResult
    out_of_sample: ValidationRunResult
    degradation_metrics: dict[str, float]
    stability_score: float

    def to_dict(self) -> dict[str, Any]:
        """Return serializable out-of-sample output."""
        return {
            "strategy_name": self.strategy_name,
            "in_sample": self.in_sample.to_dict(),
            "out_of_sample": self.out_of_sample.to_dict(),
            "degradation_metrics": self.degradation_metrics,
            "stability_score": self.stability_score,
        }


@dataclass(frozen=True)
class ParameterSweepResult:
    """One parameter-combination evaluation."""

    parameters: dict[str, Any]
    result: ValidationRunResult
    stability_metrics: dict[str, float | int]

    def to_dict(self) -> dict[str, Any]:
        """Return serializable parameter sweep result."""
        return {
            "parameters": self.parameters,
            "result": self.result.to_dict(),
            "stability_metrics": self.stability_metrics,
        }


@dataclass(frozen=True)
class ParameterSweepSummary:
    """Collected parameter sweep analysis."""

    strategy_name: str
    results: list[ParameterSweepResult]
    best_parameter_sets: list[dict[str, Any]]
    worst_parameter_sets: list[dict[str, Any]]
    stable_parameter_regions: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Return serializable sweep summary."""
        return {
            "strategy_name": self.strategy_name,
            "results": [result.to_dict() for result in self.results],
            "best_parameter_sets": self.best_parameter_sets,
            "worst_parameter_sets": self.worst_parameter_sets,
            "stable_parameter_regions": self.stable_parameter_regions,
        }


@dataclass(frozen=True)
class RobustnessScore:
    """Explainable robustness score."""

    score: float
    category: RobustnessCategory
    components: dict[str, float]
    explanation: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return serializable robustness score."""
        return {
            "score": self.score,
            "category": self.category.value,
            "components": self.components,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class OverfittingWarning:
    """One overfitting diagnostic warning."""

    code: str
    severity: WarningSeverity
    message: str
    evidence: dict[str, float | int | str]

    def to_dict(self) -> dict[str, Any]:
        """Return serializable warning."""
        return {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class ResearchValidationReport:
    """Complete reproducible strategy validation report."""

    report_id: str
    strategy_name: str
    dataset: DatasetDescriptor
    parameters: dict[str, Any]
    validation_results: dict[str, Any]
    robustness: RobustnessScore
    overfitting_warnings: list[OverfittingWarning]
    conclusions: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return serializable report."""
        return {
            "report_id": self.report_id,
            "strategy_name": self.strategy_name,
            "dataset": self.dataset.to_dict(),
            "parameters": self.parameters,
            "validation_results": self.validation_results,
            "robustness": self.robustness.to_dict(),
            "overfitting_warnings": [warning.to_dict() for warning in self.overfitting_warnings],
            "conclusions": self.conclusions,
        }
