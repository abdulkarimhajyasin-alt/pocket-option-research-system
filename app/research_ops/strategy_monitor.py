"""Strategy status monitor."""

from __future__ import annotations

from typing import Any

from app.research_ops.models import StrategyStatus


class StrategyMonitor:
    """Track readiness, gates, quality, confidence stability, and lifecycle quality."""

    def evaluate(self, readiness: dict[str, Any], lifecycle: dict[str, Any]) -> StrategyStatus:
        summary = readiness.get("summary", {})
        latest = readiness.get("latest", {})
        stability = latest.get("stability", {}) if isinstance(latest, dict) else {}
        lifecycle_summary = lifecycle.get("summary", {})
        return StrategyStatus(
            readiness_score=self._float(summary.get("readiness_score")),
            readiness_state=str(summary.get("readiness_state") or "غير متاح"),
            passed_gates=int(self._float(summary.get("passed_gates"))),
            warnings=int(self._float(summary.get("warnings"))),
            failures=int(self._float(summary.get("failures"))),
            research_quality=self._float(summary.get("readiness_score")),
            confidence_stability=self._float(stability.get("confidence_reliability")),
            lifecycle_quality=self._float(lifecycle_summary.get("average_quality")),
        )

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
