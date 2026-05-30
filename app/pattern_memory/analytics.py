"""Pattern memory analytics."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.pattern_memory.models import PatternMemoryResult


class PatternAnalytics:
    """Compute summary metrics and distributions for pattern memory."""

    def summarize(self, result: PatternMemoryResult) -> dict[str, Any]:
        records = result.records
        total = len(records)
        successful = sum(1 for row in records if row.outcome_bucket == "successful")
        failed = sum(1 for row in records if row.outcome_bucket == "failed")
        best = result.discovered_patterns[0] if result.discovered_patterns else None
        reliability = round(successful / total * 100, 2) if total else 0.0
        stability = self._average(pattern.stability for pattern in result.discovered_patterns)
        learning = self._learning_score(result)
        adaptation = self._adaptation_score(result)
        return {
            "summary": {
                "pattern_count": total,
                "successful_patterns": successful,
                "failed_patterns": failed,
                "success_ratio": reliability,
                "failure_ratio": round(failed / total * 100, 2) if total else 0.0,
                "stability_score": stability,
                "reliability_score": reliability,
                "learning_score": learning,
                "adaptation_score": adaptation,
                "best_pattern": best.description if best else "غير متاح",
                "research_only": True,
            },
            "best_pattern": best.to_dict() if best else {},
            "pattern_rankings": {
                pattern.description: pattern.pattern_score
                for pattern in result.discovered_patterns[:10]
            },
            "session_rankings": self._ranking_distribution(result, "أفضل الجلسات"),
            "asset_rankings": self._ranking_distribution(result, "أفضل الأصول"),
            "structure_rankings": self._ranking_distribution(result, "أفضل الهياكل"),
            "fvg_rankings": self._ranking_distribution(result, "أفضل أنواع FVG"),
            "cisd_rankings": self._ranking_distribution(result, "أفضل أنواع CISD"),
            "similarity_distribution": dict(
                Counter(item.category for item in result.similarities)
            ),
            "learning_progress": dict(
                Counter(item.category for item in result.learning_insights)
            ),
            "pattern_quality": {
                item.pattern_key: item.score for item in result.quality_scores[:10]
            },
            "reliability_timeline": self._timeline(records),
            "stability_distribution": {
                item.pattern_key: item.stability for item in result.quality_scores[:10]
            },
            "adaptation_analysis": {
                item.title: index + 1
                for index, item in enumerate(result.learning_insights[:10])
            },
            "latest": result.to_dict(),
        }

    def _ranking_distribution(
        self,
        result: PatternMemoryResult,
        category: str,
    ) -> dict[str, float]:
        return {
            item.name: item.score for item in result.rankings if item.category == category
        }

    def _timeline(self, records: tuple[Any, ...]) -> dict[str, float]:
        timeline = {}
        wins = 0
        for index, record in enumerate(records, start=1):
            if record.outcome_bucket == "successful":
                wins += 1
            timeline[str(index)] = round(wins / index * 100, 2)
        return timeline

    def _learning_score(self, result: PatternMemoryResult) -> float:
        if not result.learning_insights:
            return 0.0
        positive = sum(
            1
            for item in result.learning_insights
            if item.category in {"يتحسن", "مستقر"}
        )
        return round(positive / len(result.learning_insights) * 100, 2)

    def _adaptation_score(self, result: PatternMemoryResult) -> float:
        quality = self._average(item.score for item in result.quality_scores)
        similarity = self._average(item.similarity_score for item in result.similarities)
        return round((quality + similarity) / 2, 2) if result.quality_scores else 0.0

    def _average(self, values: object) -> float:
        numbers = [float(value) for value in values]
        return round(sum(numbers) / len(numbers), 2) if numbers else 0.0
