"""Execution-readiness gates for research-only candidate qualification."""

from __future__ import annotations

from typing import Any

from app.execution_readiness.models import (
    FAIL,
    PASS,
    WARNING,
    ExecutionCandidate,
    ExecutionGateResult,
    ExecutionReadinessResult,
)
from app.execution_readiness.scoring import average, clamp_score


class ExecutionGateEngine:
    """Evaluate safety gates without executing or controlling any broker."""

    def evaluate(
        self,
        candidates: tuple[ExecutionCandidate, ...],
        readiness: ExecutionReadinessResult,
        context: dict[str, Any],
    ) -> tuple[ExecutionGateResult, ...]:
        confidence = average([item.confidence for item in candidates], 0.0)
        quality = average([item.quality for item in candidates], 0.0)
        confluence = average([item.confluence for item in candidates], 0.0)
        regime = clamp_score(context.get("regime_score", readiness.regime_readiness))
        certification = clamp_score(context.get("certification_score", 70.0))
        stability = average(
            [
                readiness.signal_readiness,
                context.get("performance_score", readiness.score),
                context.get("lifecycle_score", readiness.score),
            ]
        )
        gates = (
            ("confidence", "بوابة الثقة", confidence),
            ("quality", "بوابة الجودة", quality),
            ("confluence", "بوابة التوافق", confluence),
            ("regime", "بوابة حالة السوق", regime),
            ("certification", "بوابة الاعتماد", certification),
            ("stability", "بوابة الاستقرار", stability),
        )
        return tuple(
            ExecutionGateResult(
                name=name,
                arabic_label=label,
                state=self._state(score),
                score=score,
                detail=self._detail(label, score),
            )
            for name, label, score in gates
        )

    def _state(self, score: float) -> str:
        if score >= 75:
            return PASS
        if score >= 55:
            return WARNING
        return FAIL

    def _detail(self, label: str, score: float) -> str:
        if score >= 75:
            return f"{label} ناجحة للبحث فقط."
        if score >= 55:
            return f"{label} تحتاج مراجعة قبل أي طبقة ورقية مستقبلية."
        return f"{label} غير كافية للجاهزية البحثية."
