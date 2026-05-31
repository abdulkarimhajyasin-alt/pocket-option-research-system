"""Validation for research-only execution readiness outputs."""

from __future__ import annotations

from app.execution_readiness.models import (
    FAIL,
    ExecutionCandidate,
    ExecutionGateResult,
    ExecutionReadinessResult,
    ExecutionScoringResult,
    ExecutionValidationResult,
)
from app.execution_readiness.scoring import average


class ExecutionReadinessValidation:
    """Validate candidate, readiness, gate, and score consistency."""

    def validate(
        self,
        candidates: tuple[ExecutionCandidate, ...],
        readiness: ExecutionReadinessResult,
        gates: tuple[ExecutionGateResult, ...],
        scoring: ExecutionScoringResult,
    ) -> ExecutionValidationResult:
        candidate_integrity = (
            100.0
            if candidates and all(self._valid_candidate(item) for item in candidates)
            else 0.0
        )
        readiness_integrity = 100.0 if 0 <= readiness.score <= 100 else 0.0
        gate_consistency = (
            100.0
            if gates and all(gate.state in {"PASS", "WARNING", FAIL} for gate in gates)
            else 0.0
        )
        scores = scoring.to_dict().values()
        score_consistency = 100.0 if all(0 <= value <= 100 for value in scores) else 0.0
        return ExecutionValidationResult(
            score=average(
                [
                    candidate_integrity,
                    readiness_integrity,
                    gate_consistency,
                    score_consistency,
                ]
            ),
            candidate_integrity=candidate_integrity,
            readiness_integrity=readiness_integrity,
            gate_consistency=gate_consistency,
            score_consistency=score_consistency,
        )

    def _valid_candidate(self, candidate: ExecutionCandidate) -> bool:
        return bool(candidate.candidate_id and candidate.signal_id and candidate.asset) and all(
            0 <= value <= 100
            for value in (
                candidate.confidence,
                candidate.quality,
                candidate.confluence,
                candidate.readiness,
            )
        )
