"""Paper control center aggregation."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.paper_control_center.models import PaperControlCenter


class PaperControlCenterEngine:
    """Build the executive paper-only control center model."""

    def build(
        self,
        health: dict[str, Any],
        monitoring: dict[str, Any],
        governance_status: str,
        decision: dict[str, Any],
        warning_count: int,
        recommendation_count: int,
        metadata: dict[str, Any],
    ) -> PaperControlCenter:
        overall = self._average(
            [
                health.get("health_score", 0.0),
                monitoring.get("monitoring_score", 0.0),
                health.get("portfolio_health", 0.0),
                health.get("stability_health", 0.0),
            ]
        )
        return PaperControlCenter(
            control_id="paper_control_center_0001",
            generated_at=datetime.now(UTC).isoformat(),
            portfolio_health=self._score(health.get("portfolio_health")),
            portfolio_stability=self._score(health.get("stability_health")),
            execution_status=self._status(health.get("execution_health")),
            readiness_status=self._status(health.get("readiness_health")),
            governance_status=governance_status,
            risk_status=self._status(health.get("governance_health")),
            recommendation_count=recommendation_count,
            warning_count=warning_count,
            overall_score=overall,
            metadata={**metadata, "decision": decision.get("arabic_label")},
        )

    def _status(self, score: Any) -> str:
        numeric = self._score(score)
        if numeric >= 70:
            return "PASS"
        if numeric >= 50:
            return "WARNING"
        return "FAIL"

    def _average(self, values: list[Any]) -> float:
        scores = [self._score(value) for value in values]
        return round(sum(scores) / len(scores), 2) if scores else 0.0

    def _score(self, value: Any) -> float:
        try:
            return round(max(0.0, min(100.0, float(value))), 2)
        except (TypeError, ValueError):
            return 0.0
