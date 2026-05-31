"""Readiness evaluation for research-only execution candidates."""

from __future__ import annotations

from typing import Any

from app.execution_readiness.models import ExecutionCandidate, ExecutionReadinessResult
from app.execution_readiness.scoring import average, clamp_score


class ExecutionReadinessEngine:
    """Evaluate readiness without execution or broker interaction."""

    def evaluate(
        self,
        candidates: tuple[ExecutionCandidate, ...],
        context: dict[str, Any],
    ) -> ExecutionReadinessResult:
        signal_readiness = self._signal_readiness(candidates)
        confidence_readiness = average([item.confidence for item in candidates])
        quality_readiness = average([item.quality for item in candidates])
        confluence_readiness = average([item.confluence for item in candidates])
        regime_readiness = clamp_score(context.get("regime_score", 75.0))
        pattern_readiness = clamp_score(context.get("pattern_score", 75.0))
        score = average(
            [
                signal_readiness,
                confidence_readiness,
                quality_readiness,
                confluence_readiness,
                regime_readiness,
                pattern_readiness,
            ]
        )
        return ExecutionReadinessResult(
            score=score,
            signal_readiness=signal_readiness,
            confidence_readiness=confidence_readiness,
            quality_readiness=quality_readiness,
            confluence_readiness=confluence_readiness,
            regime_readiness=regime_readiness,
            pattern_readiness=pattern_readiness,
        )

    def _signal_readiness(self, candidates: tuple[ExecutionCandidate, ...]) -> float:
        if not candidates:
            return 0.0
        actionable = [item for item in candidates if item.direction in {"CALL", "PUT"}]
        coverage = min(100.0, len(candidates) * 8.0)
        actionability = 60.0 + min(40.0, len(actionable) * 12.0)
        return average([coverage, actionability])
