"""Executive summary engine for research operations."""

from __future__ import annotations

from app.research_ops.models import ExecutiveSummary, NextAction, OpportunityStatus
from app.research_ops.models import ResearchAlert, ResearchHealth, RiskAssessment
from app.research_ops.models import StrategyStatus, PriorityRecommendation


class ExecutiveSummaryEngine:
    """Create Arabic executive summary for the research platform."""

    def build(
        self,
        strategy: StrategyStatus,
        opportunity: OpportunityStatus,
        health: ResearchHealth,
        risk: RiskAssessment,
        alerts: tuple[ResearchAlert, ...],
        recommendations: tuple[PriorityRecommendation, ...],
        next_action: NextAction,
    ) -> ExecutiveSummary:
        strategic = recommendations[0].title if recommendations else "متابعة البحث"
        return ExecutiveSummary(
            best_opportunity=opportunity.top_opportunity,
            readiness_status=strategy.readiness_state,
            research_health=health,
            active_alerts=len(alerts),
            strategic_recommendation=strategic,
            next_action=next_action,
            top_risk=risk.risks[0] if risk.risks else "لا توجد مخاطر بارزة",
            top_strength=self._strength(strategy, opportunity),
        )

    def _strength(self, strategy: StrategyStatus, opportunity: OpportunityStatus) -> str:
        if strategy.passed_gates > 0:
            return "وجود بوابات بحثية ناجحة"
        if opportunity.strongest_confluence > 60:
            return "توافق بحثي قابل للمتابعة"
        return "توفر بيانات بحثية قابلة للمراجعة"
