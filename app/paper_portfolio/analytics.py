"""Analytics for paper portfolio governance."""

from __future__ import annotations

from typing import Any


class PaperPortfolioAnalytics:
    """Generate dashboard-ready paper portfolio analytics."""

    def summarize(
        self,
        portfolio: Any,
        exposure: dict[str, Any],
        drawdown: dict[str, Any],
        governance: tuple[Any, ...],
        limits: tuple[Any, ...],
    ) -> dict[str, Any]:
        loss_rate = (
            round(portfolio.losses / portfolio.total_orders, 4)
            if portfolio.total_orders
            else 0.0
        )
        return {
            "win_rate": portfolio.win_rate,
            "loss_rate": loss_rate,
            "drawdown_analysis": drawdown,
            "stability_analysis": {"stability_score": portfolio.stability_score},
            "exposure_analysis": exposure,
            "governance_analysis": {
                item.status: self._count(governance, item.status)
                for item in governance
            },
            "risk_analysis": {item.status: self._count(limits, item.status) for item in limits},
            "paper_only": True,
            "research_only": True,
        }

    def _count(self, items: tuple[Any, ...], status: str) -> int:
        return sum(1 for item in items if item.status == status)
