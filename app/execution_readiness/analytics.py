"""Analytics for execution readiness reports and dashboard."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.execution_readiness.models import (
    QUALIFICATION_CONDITIONAL,
    QUALIFICATION_REJECTED,
    QUALIFICATION_QUALIFIED,
    QUALIFICATION_VERY_QUALIFIED,
    ExecutionReadinessRun,
)


class ExecutionReadinessAnalytics:
    """Generate dashboard-ready execution readiness distributions."""

    def summarize(self, result: ExecutionReadinessRun) -> dict[str, Any]:
        candidates = result.candidates
        qualifications = Counter(item.qualification for item in candidates)
        gates = Counter(item.state for item in result.gates)
        diagnostics = Counter(item.name for item in result.diagnostics)
        recommendations = Counter(item.title for item in result.recommendations)
        readiness = {item.candidate_id: item.readiness for item in candidates[:20]}
        confidence = {item.candidate_id: item.confidence for item in candidates[:20]}
        quality = {item.candidate_id: item.quality for item in candidates[:20]}
        confluence = {item.candidate_id: item.confluence for item in candidates[:20]}
        activity = Counter(item.timestamp[:10] for item in candidates if item.timestamp)
        rejected = Counter(
            self._rejection_reason(item)
            for item in candidates
            if item.qualification == QUALIFICATION_REJECTED
        )
        qualified = qualifications.get(QUALIFICATION_QUALIFIED, 0) + qualifications.get(
            QUALIFICATION_VERY_QUALIFIED,
            0,
        )
        return {
            "summary": {
                "candidate_count": len(candidates),
                "qualified_count": qualified,
                "conditional_count": qualifications.get(QUALIFICATION_CONDITIONAL, 0),
                "rejected_count": qualifications.get(QUALIFICATION_REJECTED, 0),
                "average_readiness": result.scoring.readiness_score,
                "average_confidence": result.scoring.confidence_score,
                "warning_count": len(result.diagnostics),
                "recommendation_count": len(result.recommendations),
                "qualification_state": result.qualification.state,
                "research_only": True,
                "readiness_only": True,
                "not_execution": True,
            },
            "readiness_distribution": readiness,
            "qualification_distribution": dict(qualifications),
            "confidence_distribution": confidence,
            "quality_distribution": quality,
            "confluence_distribution": confluence,
            "gate_distribution": dict(gates),
            "rejection_reasons": dict(rejected),
            "warning_distribution": dict(diagnostics),
            "recommendation_distribution": dict(recommendations),
            "time_activity": dict(activity),
            "latest": result.to_dict(),
        }

    def _rejection_reason(self, candidate: Any) -> str:
        if candidate.confidence < 50:
            return "الثقة منخفضة"
        if candidate.quality < 50:
            return "الجودة منخفضة"
        if candidate.confluence < 50:
            return "التوافق منخفض"
        return "الجاهزية منخفضة"
