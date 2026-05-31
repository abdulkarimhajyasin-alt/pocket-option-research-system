"""Paper control governance and decision logic."""

from __future__ import annotations

from typing import Any

from app.paper_control_center.models import (
    DECISION_CONTINUE,
    DECISION_PAUSE,
    DECISION_REVIEW,
    FAIL,
    PASS,
    WARNING,
    ControlGate,
)


class PaperControlGovernanceEngine:
    """Evaluate paper governance without controlling anything."""

    def evaluate(
        self,
        health: dict[str, Any],
        monitoring: dict[str, Any],
    ) -> tuple[ControlGate, ...]:
        return (
            self._gate(
                "portfolio_governance",
                "حوكمة المحفظة",
                health["portfolio_health"],
                70,
            ),
            self._gate(
                "execution_governance",
                "حوكمة التنفيذ الورقي",
                health["execution_health"],
                65,
            ),
            self._gate(
                "risk_governance",
                "حوكمة المخاطر",
                health["governance_health"],
                65,
            ),
            self._gate(
                "readiness_governance",
                "حوكمة الجاهزية",
                health["readiness_health"],
                70,
            ),
            self._gate(
                "monitoring_governance",
                "حوكمة المراقبة",
                monitoring["monitoring_score"],
                65,
            ),
        )

    def _gate(self, name: str, label: str, score: float, threshold: float) -> ControlGate:
        if score >= threshold:
            status = PASS
        elif score >= threshold - 15:
            status = WARNING
        else:
            status = FAIL
        return ControlGate(
            name=name,
            arabic_label=label,
            status=status,
            score=round(max(0.0, min(100.0, float(score))), 2),
            detail=f"{label}: {round(score, 2)}",
        )


class PaperControlDecisionEngine:
    """Generate paper-only research recommendations, not actions."""

    def decide(
        self,
        health: dict[str, Any],
        governance: tuple[ControlGate, ...],
    ) -> dict[str, Any]:
        failures = sum(1 for item in governance if item.status == FAIL)
        warnings = sum(1 for item in governance if item.status == WARNING)
        health_score = float(health.get("health_score", 0.0))
        if failures or health_score < 50:
            label = DECISION_PAUSE
            state = "PAUSE_PAPER_OPERATIONS"
        elif warnings or health_score < 70:
            label = DECISION_REVIEW
            state = "REVIEW_REQUIRED"
        else:
            label = DECISION_CONTINUE
            state = "CONTINUE_PAPER_OPERATIONS"
        return {
            "state": state,
            "arabic_label": label,
            "failure_count": failures,
            "warning_count": warnings,
            "health_score": round(health_score, 2),
            "research_recommendation_only": True,
            "paper_only": True,
            "not_control_action": True,
        }
