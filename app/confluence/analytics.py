"""Analytics for confluence research decisions."""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any

from app.confluence.models import ResearchDecision


class ConfluenceAnalytics:
    """Build deterministic confluence analytics and rankings."""

    def summarize(self, decisions: list[ResearchDecision]) -> dict[str, Any]:
        scores = [item.confluence_score for item in decisions]
        strong = [
            item
            for item in decisions
            if item.confluence.state in {"استثنائية", "قوية جدا", "قوية"}
        ]
        rejected = [item for item in decisions if item.confluence.state == "مرفوضة"]
        return {
            "summary": {
                "confluent_count": len(decisions),
                "average_confluence": round(mean(scores), 2) if scores else 0.0,
                "highest_confluence": round(max(scores), 2) if scores else 0.0,
                "lowest_confluence": round(min(scores), 2) if scores else 0.0,
                "strong_count": len(strong),
                "rejected_count": len(rejected),
                "research_only": True,
            },
            "confluence_distribution": self._distribution(decisions),
            "factor_contribution": self._factor_contribution(decisions),
            "asset_ranking": self._average_by(decisions, "asset"),
            "session_ranking": self._average_session(decisions),
            "timeframe_ranking": self._timeframe_ranking(decisions),
            "rejection_analysis": self._rejections(decisions),
            "quality_analysis": self._quality(decisions),
            "timeline": self._timeline(decisions),
            "latest": [item.to_dict() for item in decisions[:20]],
            "best_decision": max(
                decisions,
                key=lambda item: item.confluence_score,
            ).to_dict()
            if decisions
            else {},
        }

    def _distribution(self, decisions: list[ResearchDecision]) -> dict[str, int]:
        return dict(Counter(item.confluence.state for item in decisions))

    def _factor_contribution(self, decisions: list[ResearchDecision]) -> dict[str, float]:
        values: dict[str, list[float]] = defaultdict(list)
        for decision in decisions:
            for factor in decision.confluence.factors:
                values[factor.name].append(factor.score)
        return {key: round(mean(items), 2) for key, items in sorted(values.items())}

    def _average_by(
        self,
        decisions: list[ResearchDecision],
        field: str,
    ) -> dict[str, float]:
        values: dict[str, list[float]] = defaultdict(list)
        for decision in decisions:
            values[str(getattr(decision, field))].append(decision.confluence_score)
        return {key: round(mean(items), 2) for key, items in values.items()}

    def _average_session(self, decisions: list[ResearchDecision]) -> dict[str, float]:
        values: dict[str, list[float]] = defaultdict(list)
        for decision in decisions:
            values[decision.confluence.session].append(decision.confluence_score)
        return {key: round(mean(items), 2) for key, items in values.items()}

    def _timeframe_ranking(self, decisions: list[ResearchDecision]) -> dict[str, float]:
        values: dict[str, list[float]] = defaultdict(list)
        for decision in decisions:
            metric = next(
                (
                    factor.metrics.get("alignment_score")
                    for factor in decision.confluence.factors
                    if factor.name == "عامل الأطر الزمنية"
                ),
                0.0,
            )
            for timeframe in ("M1", "M5", "M15", "H1"):
                values[timeframe].append(float(metric))
        return {key: round(mean(items), 2) for key, items in values.items()}

    def _rejections(self, decisions: list[ResearchDecision]) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for decision in decisions:
            for reason in decision.rejection_reasons or ["لا توجد أسباب رفض"]:
                counter[str(reason)] += 1
        return dict(counter)

    def _quality(self, decisions: list[ResearchDecision]) -> dict[str, float]:
        return {
            "جودة الإشارة": self._factor_average(decisions, "عامل الإشارة"),
            "جودة الأداء": self._factor_average(decisions, "عامل الأداء"),
            "جودة الفرصة": self._factor_average(decisions, "عامل الفرصة"),
            "جودة الأطر الزمنية": self._factor_average(
                decisions,
                "عامل الأطر الزمنية",
            ),
            "جودة التوافق": round(
                mean([item.confluence_score for item in decisions]),
                2,
            )
            if decisions
            else 0.0,
        }

    def _factor_average(
        self,
        decisions: list[ResearchDecision],
        factor_name: str,
    ) -> float:
        values = [
            factor.score
            for decision in decisions
            for factor in decision.confluence.factors
            if factor.name == factor_name
        ]
        return round(mean(values), 2) if values else 0.0

    def _timeline(self, decisions: list[ResearchDecision]) -> dict[str, float]:
        values: dict[str, list[float]] = defaultdict(list)
        for decision in decisions:
            values[decision.confluence.timestamp.strftime("%H:%M")].append(
                decision.confluence_score
            )
        return {key: round(mean(items), 2) for key, items in sorted(values.items())}
