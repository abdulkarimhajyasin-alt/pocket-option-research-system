"""Paper-only portfolio limits."""

from __future__ import annotations

from typing import Any

from app.paper_portfolio.models import FAIL, PASS, WARNING, PortfolioGateResult


class PaperLimitEngine:
    """Evaluate configurable paper-only portfolio limits."""

    max_active_paper_orders = 5
    max_exposure_per_asset = 0.6
    max_exposure_per_session = 0.8
    max_drawdown = 4.0
    max_consecutive_losses = 3

    def evaluate(
        self,
        portfolio: Any,
        exposure: dict[str, Any],
        drawdown: dict[str, Any],
        results: list[dict[str, Any]],
    ) -> tuple[PortfolioGateResult, ...]:
        return (
            self._limit_gate(
                "max_active_paper_orders",
                "حد الأوامر الورقية النشطة",
                self.max_active_paper_orders - portfolio.active_orders,
            ),
            self._ratio_gate(
                "max_exposure_per_asset",
                "حد التعرض لكل أصل",
                max(exposure.get("asset_exposure", {}).values(), default=0),
                portfolio.total_orders,
                self.max_exposure_per_asset,
            ),
            self._ratio_gate(
                "max_exposure_per_session",
                "حد التعرض لكل جلسة",
                max(exposure.get("session_exposure", {}).values(), default=0),
                portfolio.total_orders,
                self.max_exposure_per_session,
            ),
            self._limit_gate(
                "max_drawdown",
                "حد السحب الورقي",
                self.max_drawdown - self._float(drawdown.get("maximum_drawdown")),
            ),
            self._limit_gate(
                "max_consecutive_losses",
                "حد الخسائر المتتالية",
                self.max_consecutive_losses - self._consecutive_losses(results),
            ),
        )

    def _ratio_gate(
        self,
        name: str,
        label: str,
        count: int,
        total: int,
        limit: float,
    ) -> PortfolioGateResult:
        ratio = count / total if total else 0.0
        margin = limit - ratio
        return self._limit_gate(name, label, margin * 100.0)

    def _limit_gate(self, name: str, label: str, margin: float) -> PortfolioGateResult:
        status = PASS if margin >= 0 else WARNING if margin >= -1 else FAIL
        score = 100.0 if status == PASS else 65.0 if status == WARNING else 25.0
        return PortfolioGateResult(
            name=name,
            arabic_label=label,
            status=status,
            score=score,
            detail=f"{label}: هامش ورقي {round(margin, 2)}",
        )

    def _consecutive_losses(self, results: list[dict[str, Any]]) -> int:
        count = 0
        for result in reversed(results):
            if result.get("outcome") == "LOSS":
                count += 1
            else:
                break
        return count

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
