"""Analytics for qualified research opportunities."""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any

from app.opportunity_engine.models import OpportunityRanking, QualifiedOpportunity


class OpportunityAnalytics:
    """Aggregate qualification and ranking metrics."""

    def summarize(
        self,
        opportunities: list[QualifiedOpportunity],
        rankings: list[OpportunityRanking],
    ) -> dict[str, Any]:
        scores = [item.qualification_score for item in opportunities]
        confidences = [item.confidence for item in opportunities]
        states = Counter(item.qualification_state for item in opportunities)
        rejected = [item for item in opportunities if item.qualification_state == "مرفوضة"]
        return {
            "summary": {
                "opportunity_count": len(opportunities),
                "average_score": round(mean(scores), 2) if scores else 0.0,
                "highest_score": round(max(scores), 2) if scores else 0.0,
                "average_confidence": round(mean(confidences), 2) if confidences else 0.0,
                "highly_qualified_count": states.get("مؤهلة جدا", 0),
                "rejected_count": states.get("مرفوضة", 0),
                "research_only": True,
            },
            "rankings": [item.to_dict() for item in rankings],
            "asset_ranking": self._average_by(opportunities, "asset"),
            "session_ranking": self._average_session(opportunities),
            "structure_ranking": self._average_structure(opportunities),
            "qualification_distribution": dict(states),
            "rejection_distribution": self._rejection_distribution(rejected),
            "fvg_ranking": self._average_fvg(opportunities),
            "quality_timeline": self._timeline(opportunities),
            "best_opportunity": rankings[0].to_dict() if rankings else {},
        }

    def _average_by(
        self,
        opportunities: list[QualifiedOpportunity],
        field: str,
    ) -> dict[str, float]:
        grouped: dict[str, list[float]] = defaultdict(list)
        for item in opportunities:
            grouped[str(getattr(item, field))].append(item.qualification_score)
        return {
            key: round(mean(values), 2)
            for key, values in sorted(grouped.items(), key=lambda row: row[0])
        }

    def _average_session(self, opportunities: list[QualifiedOpportunity]) -> dict[str, float]:
        grouped: dict[str, list[float]] = defaultdict(list)
        for item in opportunities:
            session = _extract_factor(item.supporting_factors, "جلسة")
            grouped[session or "غير متاح"].append(item.session_score)
        return {key: round(mean(values), 2) for key, values in grouped.items()}

    def _average_structure(self, opportunities: list[QualifiedOpportunity]) -> dict[str, float]:
        grouped: dict[str, list[float]] = defaultdict(list)
        for item in opportunities:
            structure = _extract_factor(item.supporting_factors, "هيكل")
            grouped[structure or "غير متاح"].append(item.structure_score)
        return {key: round(mean(values), 2) for key, values in grouped.items()}

    def _average_fvg(self, opportunities: list[QualifiedOpportunity]) -> dict[str, float]:
        grouped: dict[str, list[float]] = defaultdict(list)
        for item in opportunities:
            fvg = _extract_factor(item.supporting_factors, "FVG") or "لا يوجد"
            grouped[fvg].append(item.fvg_score)
        return {key: round(mean(values), 2) for key, values in grouped.items()}

    def _rejection_distribution(
        self,
        opportunities: list[QualifiedOpportunity],
    ) -> dict[str, int]:
        counter = Counter()
        for item in opportunities:
            for reason in item.rejection_factors:
                counter[reason] += 1
        return dict(counter)

    def _timeline(self, opportunities: list[QualifiedOpportunity]) -> dict[str, float]:
        grouped: dict[str, list[float]] = defaultdict(list)
        for item in opportunities:
            grouped[item.timestamp.strftime("%H:%M")].append(item.qualification_score)
        return {key: round(mean(values), 2) for key, values in sorted(grouped.items())}


def _extract_factor(values: list[str], needle: str) -> str | None:
    for value in values:
        if needle in value:
            return value
    return None
