"""Opportunity ranking engine."""

from __future__ import annotations

from app.opportunity_engine.models import OpportunityRanking, QualifiedOpportunity


class OpportunityRankingEngine:
    """Rank opportunities by descending research quality score."""

    def rank(self, opportunities: list[QualifiedOpportunity]) -> list[OpportunityRanking]:
        ordered = sorted(
            opportunities,
            key=lambda item: (item.qualification_score, item.confidence, item.timestamp),
            reverse=True,
        )
        return [
            OpportunityRanking(
                rank=index + 1,
                opportunity=opportunity,
                reasoning=(
                    f"الترتيب {index + 1} بسبب درجة فرصة "
                    f"{opportunity.qualification_score:.2f}."
                ),
            )
            for index, opportunity in enumerate(ordered)
        ]
