"""Stability scoring for paper-to-live readiness."""

from __future__ import annotations

from typing import Any


class PaperToLiveStabilityEngine:
    """Evaluate paper, drawdown, governance, readiness, and signal stream stability."""

    def evaluate(self, sources: dict[str, Any]) -> dict[str, Any]:
        paper_control = self._summary(sources.get("paper_control_center", {}))
        paper_portfolio = self._summary(sources.get("paper_portfolio", {}))
        execution_readiness = self._summary(sources.get("execution_readiness", {}))
        signal_stream = self._summary(sources.get("signal_stream", {}))
        drawdown = self._score(
            paper_portfolio.get("maximum_drawdown") or paper_portfolio.get("drawdown")
        )
        paper_score = self._score(
            paper_control.get("overall_score")
            or paper_portfolio.get("portfolio_score")
            or paper_portfolio.get("health_score")
        )
        drawdown_stability = max(0.0, 100.0 - drawdown * 10.0)
        governance_stability = self._status_score(
            paper_control.get("governance_status"),
            fallback=paper_control.get("overall_score"),
        )
        readiness_stability = self._score(
            execution_readiness.get("average_readiness")
            or execution_readiness.get("readiness_score")
        )
        signal_stability = self._score(
            signal_stream.get("quality_score")
            or signal_stream.get("stream_score")
            or signal_stream.get("average_confidence")
        )
        stability_score = round(
            (
                paper_score
                + drawdown_stability
                + governance_stability
                + readiness_stability
                + signal_stability
            )
            / 5.0,
            2,
        )
        return {
            "paper_performance_stability": round(paper_score, 2),
            "drawdown_stability": round(drawdown_stability, 2),
            "governance_stability": round(governance_stability, 2),
            "readiness_stability": round(readiness_stability, 2),
            "signal_stream_stability": round(signal_stability, 2),
            "stability_score": stability_score,
            "readiness_only": True,
        }

    def _summary(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return {}
        summary = payload.get("summary", payload)
        return summary if isinstance(summary, dict) else {}

    def _status_score(self, value: Any, fallback: Any = None) -> float:
        mapping = {"PASS": 100.0, "WARNING": 60.0, "FAIL": 0.0}
        return mapping.get(str(value), self._score(fallback))

    def _score(self, value: Any) -> float:
        try:
            return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return 0.0
