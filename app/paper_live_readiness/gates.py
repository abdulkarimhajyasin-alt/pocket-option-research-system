"""Readiness gate evaluation."""

from __future__ import annotations

from app.paper_live_readiness.models import FAIL, PASS, WARNING, ReadinessGate


class PaperToLiveGateEngine:
    """Evaluate readiness gates without granting live-trading approval."""

    def evaluate(
        self,
        readiness_scores: dict[str, float],
        safety: dict[str, object],
    ) -> tuple[ReadinessGate, ...]:
        return (
            self._gate(
                "paper_performance_gate",
                "بوابة الأداء الورقي",
                readiness_scores["paper_health"],
                75,
            ),
            self._gate(
                "portfolio_stability_gate",
                "بوابة استقرار المحفظة",
                readiness_scores["paper_stability"],
                75,
            ),
            self._gate(
                "governance_gate",
                "بوابة الحوكمة",
                readiness_scores["paper_governance"],
                80,
            ),
            self._gate(
                "execution_readiness_gate",
                "بوابة جاهزية التنفيذ",
                readiness_scores["execution_readiness"],
                75,
            ),
            self._gate(
                "observation_readiness_gate",
                "بوابة جاهزية المراقبة",
                readiness_scores["observation_readiness"],
                75,
            ),
            self._gate(
                "certification_gate",
                "بوابة الاعتماد البحثي",
                readiness_scores["certification_score"],
                75,
            ),
            self._gate(
                "safety_gate",
                "بوابة السلامة",
                float(safety.get("safety_score", 0.0)),
                100,
            ),
        )

    def _gate(
        self,
        name: str,
        label: str,
        score: float,
        threshold: float,
    ) -> ReadinessGate:
        if score >= threshold:
            status = PASS
        elif score >= threshold - 15:
            status = WARNING
        else:
            status = FAIL
        return ReadinessGate(
            name=name,
            arabic_label=label,
            status=status,
            score=round(max(0.0, min(100.0, float(score))), 2),
            detail=f"{label}: {round(score, 2)}",
        )
