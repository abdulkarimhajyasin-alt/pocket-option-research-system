"""Paper-only drawdown analysis."""

from __future__ import annotations

from typing import Any


class PaperDrawdownEngine:
    """Calculate simulated paper drawdown without real money."""

    def evaluate(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        equity = 0.0
        peak = 0.0
        current_drawdown = 0.0
        max_drawdown = 0.0
        curve = []
        for result in results:
            equity += self._float(result.get("simulated_return"))
            peak = max(peak, equity)
            current_drawdown = max(0.0, peak - equity)
            max_drawdown = max(max_drawdown, current_drawdown)
            curve.append(round(equity, 2))
        recovery_factor = round((equity / max_drawdown), 2) if max_drawdown else 100.0
        trend = "مستقر" if current_drawdown <= max_drawdown / 2 else "متزايد"
        score = max(0.0, min(100.0, 100.0 - (max_drawdown * 20.0)))
        return {
            "current_drawdown": round(current_drawdown, 2),
            "maximum_drawdown": round(max_drawdown, 2),
            "drawdown_trend": trend,
            "recovery_factor": recovery_factor,
            "drawdown_score": round(score, 2),
            "equity_curve": curve,
            "paper_only": True,
        }

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
