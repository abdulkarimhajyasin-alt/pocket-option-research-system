"""Scoring helpers for the research-only execution readiness framework."""

from __future__ import annotations

from app.execution_readiness.models import (
    ExecutionCandidate,
    ExecutionReadinessResult,
    ExecutionScoringResult,
)


def clamp_score(value: float) -> float:
    """Clamp a numeric score into the 0-100 range."""
    return round(max(0.0, min(100.0, float(value))), 2)


def average(values: list[float] | tuple[float, ...], default: float = 0.0) -> float:
    """Return a bounded average."""
    numeric = [clamp_score(value) for value in values]
    if not numeric:
        return clamp_score(default)
    return clamp_score(sum(numeric) / len(numeric))


class ExecutionScoringEngine:
    """Generate bounded execution-readiness scores."""

    def evaluate(
        self,
        candidates: tuple[ExecutionCandidate, ...],
        readiness: ExecutionReadinessResult,
    ) -> ExecutionScoringResult:
        qualification = average([item.readiness for item in candidates], readiness.score)
        confidence = average([item.confidence for item in candidates], readiness.score)
        quality = average([item.quality for item in candidates], readiness.score)
        return ExecutionScoringResult(
            readiness_score=clamp_score(readiness.score),
            qualification_score=qualification,
            confidence_score=confidence,
            quality_score=quality,
        )
