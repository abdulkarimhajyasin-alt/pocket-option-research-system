"""Strategy benchmark ranking."""

from __future__ import annotations

from app.strategy_benchmark.models import BenchmarkScore, ComparisonResult, StrategyRanking


class StrategyRankingEngine:
    """Rank all benchmark profiles."""

    def rank(
        self,
        comparisons: tuple[ComparisonResult, ...],
        scores: tuple[BenchmarkScore, ...],
    ) -> tuple[StrategyRanking, ...]:
        comparison_by_id = {item.profile.profile_id: item for item in comparisons}
        ordered = sorted(scores, key=lambda item: item.score, reverse=True)
        rankings = []
        for index, score in enumerate(ordered, start=1):
            comparison = comparison_by_id[score.profile_id]
            strengths = [
                name for name, value in score.components.items() if value >= 70
            ]
            weaknesses = [
                name for name, value in score.components.items() if value < 60
            ]
            rankings.append(
                StrategyRanking(
                    index,
                    score.profile_id,
                    comparison.profile.profile_name,
                    score.score,
                    strengths,
                    weaknesses,
                    self._reason(score, strengths, weaknesses),
                )
            )
        return tuple(rankings)

    def _reason(
        self,
        score: BenchmarkScore,
        strengths: list[str],
        weaknesses: list[str],
    ) -> str:
        if not weaknesses:
            return "تم اختياره بسبب توازن الدرجة وقلة نقاط الضعف البحثية."
        if strengths:
            return "تم ترتيبه وفق تفوقه في " + "، ".join(strengths[:2])
        return "يحتاج تحسين قبل الاعتماد في المقارنة البحثية."
