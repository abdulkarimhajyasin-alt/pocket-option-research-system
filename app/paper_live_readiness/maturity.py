"""Maturity scoring for paper-to-live readiness."""

from __future__ import annotations

from typing import Any


class PaperToLiveMaturityEngine:
    """Evaluate sample, portfolio, readiness, certification, and observation maturity."""

    def evaluate(self, sources: dict[str, Any]) -> dict[str, Any]:
        paper_execution = self._summary(sources.get("paper_execution", {}))
        paper_portfolio = self._summary(sources.get("paper_portfolio", {}))
        execution_readiness = self._summary(sources.get("execution_readiness", {}))
        certification = self._summary(sources.get("research_certification", {}))
        observation = self._summary(sources.get("observation_intelligence", {}))
        market_observation = self._summary(sources.get("market_observation", {}))
        sample_score = min(
            100.0,
            self._score(paper_execution.get("total_orders") or paper_execution.get("order_count"))
            * 10.0,
        )
        portfolio_score = self._score(
            paper_portfolio.get("portfolio_score") or paper_portfolio.get("health_score")
        )
        readiness_score = self._score(
            execution_readiness.get("average_readiness")
            or execution_readiness.get("readiness_score")
        )
        certification_score = self._score(
            certification.get("certification_score")
            or certification.get("maturity_score")
            or certification.get("overall_score")
        )
        observation_score = max(
            self._score(observation.get("quality_score")),
            self._score(market_observation.get("quality_score")),
            self._score(market_observation.get("market_activity_score")),
        )
        maturity_score = round(
            (
                sample_score
                + portfolio_score
                + readiness_score
                + certification_score
                + observation_score
            )
            / 5.0,
            2,
        )
        return {
            "paper_sample_maturity": round(sample_score, 2),
            "portfolio_maturity": round(portfolio_score, 2),
            "readiness_maturity": round(readiness_score, 2),
            "certification_maturity": round(certification_score, 2),
            "observation_maturity": round(observation_score, 2),
            "maturity_score": maturity_score,
            "readiness_only": True,
        }

    def _summary(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return {}
        summary = payload.get("summary", payload)
        return summary if isinstance(summary, dict) else {}

    def _score(self, value: Any) -> float:
        try:
            return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return 0.0
