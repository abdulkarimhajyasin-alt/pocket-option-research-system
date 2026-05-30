"""Opportunity monitoring."""

from __future__ import annotations

from typing import Any

from app.research_ops.models import OpportunityStatus


class OpportunityMonitor:
    """Track top opportunity and strongest research factors."""

    def evaluate(
        self,
        confluence: dict[str, Any],
        lifecycle: dict[str, Any],
    ) -> OpportunityStatus:
        best = confluence.get("best_decision", {}) or confluence.get("best", {})
        lifecycle_summary = lifecycle.get("summary", {})
        confluence_payload = best.get("confluence", {}) if isinstance(best, dict) else {}
        factors = (
            confluence_payload.get("factors", [])
            if isinstance(confluence_payload, dict)
            else []
        )
        return OpportunityStatus(
            top_opportunity=str(best.get("asset") or "غير متاح")
            if isinstance(best, dict)
            else "غير متاح",
            strongest_confluence=self._float(best.get("confluence_score"))
            if isinstance(best, dict)
            else 0.0,
            strongest_alignment=self._factor_metric(
                factors,
                "عامل الأطر الزمنية",
                "alignment_score",
            ),
            strongest_session=str(lifecycle_summary.get("best_session") or "غير متاح"),
            strongest_liquidity=self._factor_metric(factors, "عامل السيولة", "liquidity_score"),
            opportunity_count=int(self._float(lifecycle_summary.get("total_lifecycles"))),
        )

    def _factor_metric(self, factors: Any, name: str, metric: str) -> float:
        if not isinstance(factors, list):
            return 0.0
        for factor in factors:
            if isinstance(factor, dict) and factor.get("name") == name:
                metrics = factor.get("metrics", {})
                return (
                    self._float(metrics.get(metric))
                    if isinstance(metrics, dict)
                    else 0.0
                )
        return 0.0

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
