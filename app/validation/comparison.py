"""Research validation comparison engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.validation.models import RobustnessScore, ValidationRunResult


@dataclass(frozen=True)
class ResearchComparisonItem:
    """One comparable strategy/configuration validation result."""

    name: str
    result: ValidationRunResult
    robustness: RobustnessScore

    def to_dict(self) -> dict[str, Any]:
        """Return serializable comparison item."""
        return {
            "name": self.name,
            "result": self.result.to_dict(),
            "robustness": self.robustness.to_dict(),
        }


class ResearchComparisonEngine:
    """Ranks validation runs using robustness and stability, not profitability alone."""

    def compare(
        self,
        items: list[ResearchComparisonItem],
    ) -> dict[str, Any]:
        """Return rankings and cross-run comparisons."""
        ranked = sorted(
            items,
            key=lambda item: (
                item.robustness.score,
                item.result.metrics.average_confidence,
                item.result.metrics.signal_count,
                item.result.metrics.net_pnl,
            ),
            reverse=True,
        )
        return {
            "rankings": [
                {
                    "rank": index + 1,
                    "name": item.name,
                    "robustness_score": item.robustness.score,
                    "category": item.robustness.category.value,
                    "signal_count": item.result.metrics.signal_count,
                    "average_confidence": item.result.metrics.average_confidence,
                    "net_pnl": item.result.metrics.net_pnl,
                }
                for index, item in enumerate(ranked)
            ],
            "items": [item.to_dict() for item in items],
        }
