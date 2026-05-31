"""Qualification engine for research-only execution readiness."""

from __future__ import annotations

from collections import Counter

from app.execution_readiness.models import (
    ExecutionCandidate,
    ExecutionQualificationResult,
    QUALIFICATION_CONDITIONAL,
    QUALIFICATION_QUALIFIED,
    QUALIFICATION_REJECTED,
    QUALIFICATION_VERY_QUALIFIED,
    QUALIFICATION_WEAK,
)
from app.execution_readiness.scoring import average


class ExecutionQualificationEngine:
    """Classify candidates into Arabic qualification states."""

    def qualify_score(self, score: float) -> str:
        if score >= 95:
            return QUALIFICATION_VERY_QUALIFIED
        if score >= 85:
            return QUALIFICATION_QUALIFIED
        if score >= 70:
            return QUALIFICATION_CONDITIONAL
        if score >= 50:
            return QUALIFICATION_WEAK
        return QUALIFICATION_REJECTED

    def evaluate(
        self,
        candidates: tuple[ExecutionCandidate, ...],
    ) -> ExecutionQualificationResult:
        distribution = Counter(item.qualification for item in candidates)
        score = average([item.readiness for item in candidates], 0.0)
        return ExecutionQualificationResult(
            score=score,
            state=self.qualify_score(score),
            distribution=dict(distribution),
        )
