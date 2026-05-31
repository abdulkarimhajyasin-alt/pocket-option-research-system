"""Readiness scoring engine for paper-to-live assessment."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.paper_live_readiness.models import (
    STATE_ADVANCED_OBSERVATION,
    STATE_LIMITED_IMPROVEMENT,
    STATE_MAJOR_IMPROVEMENT,
    STATE_NOT_QUALIFIED,
    STATE_STRICT_CONDITIONS,
    PaperToLiveReadiness,
)


class PaperToLiveReadinessEngine:
    """Evaluate readiness without approving live trading or execution."""

    def evaluate(
        self,
        sources: dict[str, Any],
        safety: dict[str, Any],
        maturity: dict[str, Any],
        stability: dict[str, Any],
        metadata: dict[str, bool],
    ) -> PaperToLiveReadiness:
        paper_control = self._summary(sources.get("paper_control_center", {}))
        paper_portfolio = self._summary(sources.get("paper_portfolio", {}))
        execution_readiness = self._summary(sources.get("execution_readiness", {}))
        broker_readiness = self._summary(sources.get("broker_readiness", {}))
        certification = self._summary(sources.get("research_certification", {}))
        observation = self._summary(sources.get("observation_intelligence", {}))
        market_observation = self._summary(sources.get("market_observation", {}))
        paper_health = self._score(
            paper_control.get("portfolio_health")
            or paper_portfolio.get("health_score")
            or paper_portfolio.get("portfolio_score")
        )
        paper_stability = self._score(
            paper_control.get("portfolio_stability")
            or paper_portfolio.get("stability_score")
            or stability.get("stability_score")
        )
        paper_governance = self._status_score(
            paper_control.get("governance_status"),
            fallback=paper_control.get("overall_score"),
        )
        execution_score = self._score(
            paper_control.get("execution_readiness")
            or execution_readiness.get("average_readiness")
            or execution_readiness.get("readiness_score")
        )
        observation_score = max(
            self._score(broker_readiness.get("readiness_score")),
            self._score(observation.get("quality_score")),
            self._score(market_observation.get("quality_score")),
            self._score(market_observation.get("market_activity_score")),
        )
        certification_score = self._score(
            certification.get("certification_score")
            or certification.get("maturity_score")
            or certification.get("overall_score")
        )
        safety_score = self._score(safety.get("safety_score"))
        maturity_score = self._score(maturity.get("maturity_score"))
        overall = self._weighted(
            (
                paper_health,
                paper_stability,
                paper_governance,
                execution_score,
                observation_score,
                certification_score,
                safety_score,
                maturity_score,
            )
        )
        return PaperToLiveReadiness(
            readiness_id=f"paper_live_readiness_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            generated_at=datetime.now(UTC).isoformat(),
            paper_health=paper_health,
            paper_stability=paper_stability,
            paper_governance=paper_governance,
            execution_readiness=execution_score,
            observation_readiness=observation_score,
            certification_score=certification_score,
            safety_score=safety_score,
            maturity_score=maturity_score,
            overall_score=overall,
            readiness_state=self.state_for_score(overall),
            metadata=metadata,
        )

    def state_for_score(self, score: float) -> str:
        """Return Arabic readiness state by score band."""
        if score >= 95:
            return STATE_ADVANCED_OBSERVATION
        if score >= 85:
            return STATE_STRICT_CONDITIONS
        if score >= 70:
            return STATE_LIMITED_IMPROVEMENT
        if score >= 50:
            return STATE_MAJOR_IMPROVEMENT
        return STATE_NOT_QUALIFIED

    def explanation_for_score(self, score: float) -> str:
        """Return Arabic explanation for the readiness band."""
        if score >= 95:
            return "النتائج الورقية ناضجة بما يكفي لدراسة مراقبة متقدمة فقط."
        if score >= 85:
            return "النتائج جيدة لكن أي مرحلة لاحقة تحتاج شروط سلامة صارمة."
        if score >= 70:
            return "المنظومة واعدة لكنها تحتاج تحسينات محدودة قبل أي تحضير لاحق."
        if score >= 50:
            return "المنظومة تحتاج تحسينات كبيرة في الورقي والحوكمة والمراقبة."
        return "المنظومة غير مؤهلة لأي مرحلة لاحقة ويجب تحسين الأساس البحثي."

    def _summary(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return {}
        summary = payload.get("summary", payload)
        return summary if isinstance(summary, dict) else {}

    def _weighted(self, scores: tuple[float, ...]) -> float:
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 2)

    def _status_score(self, value: Any, fallback: Any = None) -> float:
        mapping = {"PASS": 100.0, "WARNING": 60.0, "FAIL": 0.0}
        return mapping.get(str(value), self._score(fallback))

    def _score(self, value: Any) -> float:
        try:
            return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return 0.0
