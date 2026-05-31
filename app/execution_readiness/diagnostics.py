"""Diagnostics and recommendations for execution readiness."""

from __future__ import annotations

from app.execution_readiness.models import (
    FAIL,
    WARNING,
    ExecutionCandidate,
    ExecutionDiagnostic,
    ExecutionGateResult,
    ExecutionReadinessResult,
    ExecutionRecommendation,
)
from app.execution_readiness.scoring import average


class ExecutionReadinessDiagnostics:
    """Detect weak readiness dimensions."""

    def evaluate(
        self,
        candidates: tuple[ExecutionCandidate, ...],
        readiness: ExecutionReadinessResult,
        gates: tuple[ExecutionGateResult, ...],
    ) -> tuple[ExecutionDiagnostic, ...]:
        diagnostics: list[ExecutionDiagnostic] = []
        weak_candidates = [item for item in candidates if item.readiness < 70]
        checks = (
            ("ضعف الثقة", readiness.confidence_readiness, "تحسين الثقة"),
            ("ضعف الجودة", readiness.quality_readiness, "تحسين الجودة"),
            ("ضعف التوافق", readiness.confluence_readiness, "تحسين التوافق"),
            ("ضعف حالة السوق", readiness.regime_readiness, "تحسين الاستقرار"),
            ("ضعف الاعتماد", self._gate_score(gates, "certification"), "تحسين الاعتماد"),
        )
        for name, score, detail in checks:
            if score < 70:
                diagnostics.append(
                    ExecutionDiagnostic(name=name, severity="متوسط", detail=detail)
                )
        failed_gates = [gate for gate in gates if gate.state == FAIL]
        warning_gates = [gate for gate in gates if gate.state == WARNING]
        if failed_gates or warning_gates or weak_candidates:
            diagnostics.append(
                ExecutionDiagnostic(
                    name="مرشحون غير مستقرين",
                    severity="مرتفع" if failed_gates else "متوسط",
                    detail="توجد بوابات أو مرشحون يحتاجون مراجعة بحثية قبل الورق.",
                )
            )
        return tuple(diagnostics)

    def _gate_score(self, gates: tuple[ExecutionGateResult, ...], name: str) -> float:
        matches = [gate.score for gate in gates if gate.name == name]
        return average(matches, 0.0)


class ExecutionReadinessRecommendations:
    """Generate Arabic readiness recommendations."""

    def generate(
        self,
        diagnostics: tuple[ExecutionDiagnostic, ...],
    ) -> tuple[ExecutionRecommendation, ...]:
        titles = {
            "ضعف الثقة": "تحسين الثقة",
            "ضعف الجودة": "تحسين الجودة",
            "ضعف التوافق": "تحسين التوافق",
            "ضعف حالة السوق": "تحسين الاستقرار",
            "ضعف الاعتماد": "تحسين الاعتماد",
            "مرشحون غير مستقرين": "تحسين الاستقرار",
        }
        recommendations = [
            ExecutionRecommendation(
                title=titles.get(item.name, "تحسين الجاهزية"),
                priority=item.severity,
                reason=item.detail,
            )
            for item in diagnostics
        ]
        if not recommendations:
            recommendations.append(
                ExecutionRecommendation(
                    title="المتابعة البحثية",
                    priority="منخفض",
                    reason="المرشحون مستقرون ضمن إطار الجاهزية البحثية فقط.",
                )
            )
        return tuple(recommendations)
