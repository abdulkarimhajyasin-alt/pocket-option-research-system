"""Analytics summaries for validation quality research."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.validation.models import ResearchValidationReport


@dataclass(frozen=True)
class ValidationQualitySnapshot:
    """Compact validation analytics snapshot."""

    strategy_name: str
    robustness_score: float
    robustness_category: str
    warning_count: int
    high_severity_warnings: int
    dataset_sample_count: int

    def to_dict(self) -> dict[str, Any]:
        """Return serializable validation analytics."""
        return {
            "strategy_name": self.strategy_name,
            "robustness_score": self.robustness_score,
            "robustness_category": self.robustness_category,
            "warning_count": self.warning_count,
            "high_severity_warnings": self.high_severity_warnings,
            "dataset_sample_count": self.dataset_sample_count,
        }


class ValidationQualityAnalyzer:
    """Builds analytics that remain separate from execution analytics."""

    def analyze(self, report: ResearchValidationReport) -> ValidationQualitySnapshot:
        """Analyze a validation report."""
        return ValidationQualitySnapshot(
            strategy_name=report.strategy_name,
            robustness_score=report.robustness.score,
            robustness_category=report.robustness.category.value,
            warning_count=len(report.overfitting_warnings),
            high_severity_warnings=sum(
                1 for warning in report.overfitting_warnings if warning.severity.value == "high"
            ),
            dataset_sample_count=report.dataset.sample_count,
        )
