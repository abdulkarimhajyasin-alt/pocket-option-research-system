"""Strategy benchmark analytics."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.strategy_benchmark.models import StrategyBenchmarkResult


class StrategyBenchmarkAnalytics:
    """Generate benchmark distributions for reports and dashboard."""

    def summarize(self, result: StrategyBenchmarkResult) -> dict[str, Any]:
        rankings = result.rankings
        best = rankings[0] if rankings else None
        scores = {item.profile_id: item.score for item in result.scores}
        readiness = {
            item.profile.profile_name: item.readiness_score
            for item in result.comparisons
        }
        stability = {
            item.profile.profile_name: item.stability_score
            for item in result.comparisons
        }
        profile_names = {
            item.profile.profile_id: item.profile.profile_name
            for item in result.comparisons
        }
        quality = {
            profile_names.get(item.profile_id, item.profile_id): item.components.get(
                "quality",
                0,
            )
            for item in result.scores
        }
        return {
            "summary": {
                "profile_count": len(result.comparisons),
                "best_profile": best.profile_name if best else "غير متاح",
                "highest_score": best.score if best else 0.0,
                "average_performance": self._average(scores.values()),
                "highest_stability": max(stability.values()) if stability else 0.0,
                "highest_readiness": max(readiness.values()) if readiness else 0.0,
                "certification_state": result.certification.state,
                "research_only": True,
            },
            "best_profile": best.to_dict() if best else {},
            "benchmark_distribution": scores,
            "readiness_distribution": readiness,
            "stability_distribution": stability,
            "robustness_distribution": {
                item.profile_id: item.score for item in result.robustness
            },
            "improvement_distribution": dict(
                Counter(item.status_ar for item in result.improvements)
            ),
            "ranking_distribution": {
                item.profile_name: item.score for item in rankings
            },
            "quality_distribution": quality,
            "timeline": {result.timestamp.strftime("%H:%M"): best.score if best else 0.0},
            "strengths": dict(Counter(self._flatten(item.strengths for item in rankings))),
            "weaknesses": dict(Counter(self._flatten(item.weaknesses for item in rankings))),
            "improvements": {
                item.profile_id: item.score_delta for item in result.improvements
            },
            "degradations": {
                item.profile_id: item.score_delta
                for item in result.improvements
                if item.score_delta < 0
            },
            "latest": result.to_dict(),
        }

    def _flatten(self, rows: object) -> list[str]:
        values = []
        for row in rows:
            values.extend(row)
        return values

    def _average(self, values: object) -> float:
        numbers = [float(value) for value in values]
        return round(sum(numbers) / len(numbers), 2) if numbers else 0.0
