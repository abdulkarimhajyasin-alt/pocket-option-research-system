"""Paper-only portfolio governance."""

from __future__ import annotations

from typing import Any

from app.paper_portfolio.models import FAIL, PASS, WARNING, PortfolioGateResult


class PaperRiskGovernanceEngine:
    """Evaluate paper portfolio governance gates."""

    def evaluate(
        self,
        portfolio: Any,
        exposure: dict[str, Any],
        orders: list[dict[str, Any]],
        results: list[dict[str, Any]],
    ) -> tuple[PortfolioGateResult, ...]:
        average_confidence = self._average(order.get("confidence") for order in orders)
        average_readiness = self._average(order.get("readiness_score") for order in orders)
        consecutive_losses = self._consecutive_losses(results)
        return (
            self._score_gate(
                "portfolio_concentration",
                "تركيز المحفظة",
                100.0 - self._float(exposure.get("concentration")) * 100.0,
                65.0,
            ),
            self._score_gate(
                "consecutive_losses",
                "الخسائر المتتالية",
                max(0.0, 100.0 - consecutive_losses * 25.0),
                65.0,
            ),
            self._score_gate("confidence_quality", "جودة الثقة", average_confidence, 70.0),
            self._score_gate("readiness_quality", "جودة الجاهزية", average_readiness, 70.0),
            self._score_gate("candidate_quality", "جودة المرشحين", portfolio.health_score, 65.0),
            self._score_gate(
                "portfolio_stability",
                "استقرار المحفظة",
                portfolio.stability_score,
                65.0,
            ),
        )

    def _score_gate(
        self,
        name: str,
        label: str,
        score: float,
        threshold: float,
    ) -> PortfolioGateResult:
        if score >= threshold:
            status = PASS
        elif score >= threshold - 15:
            status = WARNING
        else:
            status = FAIL
        return PortfolioGateResult(
            name=name,
            arabic_label=label,
            status=status,
            score=round(max(0.0, min(100.0, score)), 2),
            detail=f"{label}: {round(score, 2)}",
        )

    def _consecutive_losses(self, results: list[dict[str, Any]]) -> int:
        count = 0
        for result in reversed(results):
            if result.get("outcome") == "LOSS":
                count += 1
            else:
                break
        return count

    def _average(self, values: Any) -> float:
        scores = [self._float(value) for value in values]
        return round(sum(scores) / len(scores), 2) if scores else 0.0

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
