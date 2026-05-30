"""Arabic benchmark recommendation engine."""

from __future__ import annotations

from app.strategy_benchmark.models import (
    BenchmarkRecommendation,
    ImprovementReport,
    RobustnessScore,
    StrategyRanking,
)


class BenchmarkRecommendationEngine:
    """Generate prioritized Arabic benchmark recommendations."""

    def generate(
        self,
        rankings: tuple[StrategyRanking, ...],
        robustness: tuple[RobustnessScore, ...],
        improvements: tuple[ImprovementReport, ...],
    ) -> tuple[BenchmarkRecommendation, ...]:
        recommendations = []
        best = rankings[0] if rankings else None
        if best:
            recommendations.append(
                BenchmarkRecommendation(
                    f"اعتماد {best.profile_name} للمقارنة البحثية",
                    "عالية",
                    best.selection_reason,
                    best.profile_id,
                )
            )
        weak_robustness = [item for item in robustness if item.score < 70]
        if weak_robustness:
            recommendations.append(
                BenchmarkRecommendation(
                    "تحسين الاستقرار",
                    "عالية",
                    "بعض الملفات تظهر متانة أقل من المستوى البحثي المطلوب.",
                )
            )
        if any(item.status == "degraded" for item in improvements):
            recommendations.append(
                BenchmarkRecommendation(
                    "تحسين التوافق",
                    "متوسطة",
                    "تم رصد تراجع في بعض الملفات مقارنة بخط الأساس.",
                )
            )
        recommendations.extend(
            [
                BenchmarkRecommendation(
                    "تحسين جودة الفرص",
                    "متوسطة",
                    "رفع جودة التأهيل يساعد المقارنة بين الملفات.",
                ),
                BenchmarkRecommendation(
                    "تحسين الثقة",
                    "متوسطة",
                    "تحتاج دقة الثقة إلى متابعة مستمرة عبر العينات.",
                ),
                BenchmarkRecommendation(
                    "زيادة البيانات",
                    "منخفضة",
                    "العينات الأوسع تقلل التباين وتدعم التكرارية.",
                ),
            ]
        )
        return tuple(recommendations)
