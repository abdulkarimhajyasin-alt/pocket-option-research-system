"""Benchmark improvement, robustness, and certification engines."""

from __future__ import annotations

from app.strategy_benchmark.models import (
    BenchmarkScore,
    CertificationPreparation,
    ComparisonResult,
    ImprovementReport,
    RobustnessScore,
)


class ImprovementDetectionEngine:
    """Detect improved, unchanged, or degraded research quality."""

    def evaluate(
        self,
        baseline: BenchmarkScore,
        scores: tuple[BenchmarkScore, ...],
        comparisons: tuple[ComparisonResult, ...],
    ) -> tuple[ImprovementReport, ...]:
        comparison_by_id = {
            item.profile.profile_id: item for item in comparisons
        }
        baseline_comparison = comparison_by_id.get(baseline.profile_id)
        reports = []
        for score in scores:
            comparison = comparison_by_id[score.profile_id]
            score_delta = round(score.score - baseline.score, 2)
            quality_delta = round(
                score.components.get("quality", 0)
                - baseline.components.get("quality", 0),
                2,
            )
            stability_delta = round(
                comparison.stability_score
                - (baseline_comparison.stability_score if baseline_comparison else 0),
                2,
            )
            readiness_delta = round(
                comparison.readiness_score
                - (baseline_comparison.readiness_score if baseline_comparison else 0),
                2,
            )
            status, status_ar = self._status(score_delta, quality_delta, stability_delta)
            reports.append(
                ImprovementReport(
                    score.profile_id,
                    status,
                    status_ar,
                    score_delta,
                    quality_delta,
                    stability_delta,
                    readiness_delta,
                )
            )
        return tuple(reports)

    def _status(
        self,
        score_delta: float,
        quality_delta: float,
        stability_delta: float,
    ) -> tuple[str, str]:
        if score_delta >= 3 and quality_delta >= 0 and stability_delta >= -2:
            return "improved", "تحسن"
        if score_delta <= -3 or quality_delta <= -4 or stability_delta <= -5:
            return "degraded", "تراجع"
        return "unchanged", "دون تغيير"


class ResearchRobustnessEngine:
    """Evaluate repeatability, stability, consistency, and variance."""

    def evaluate(
        self,
        comparisons: tuple[ComparisonResult, ...],
    ) -> tuple[RobustnessScore, ...]:
        scores = []
        for comparison in comparisons:
            values = list(comparison.adjusted_metrics.values())
            variance = round(max(values) - min(values), 2) if values else 0.0
            repeatability = self._clamp(100 - variance)
            stability = comparison.stability_score
            consistency = comparison.consistency_score
            score = self._clamp(
                repeatability * 0.35 + stability * 0.35 + consistency * 0.3
            )
            scores.append(
                RobustnessScore(
                    comparison.profile.profile_id,
                    score,
                    repeatability,
                    stability,
                    consistency,
                    variance,
                )
            )
        return tuple(scores)

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(100.0, float(value))), 2)


class ResearchCertificationPreparationEngine:
    """Prepare a research certification state without deployment approval."""

    def evaluate(
        self,
        best_score: BenchmarkScore,
        best_robustness: RobustnessScore,
    ) -> CertificationPreparation:
        if best_score.score >= 85 and best_robustness.score >= 80:
            return CertificationPreparation(
                "جاهزة للمقارنة المتقدمة",
                "المؤشرات البحثية كافية للمقارنة المتقدمة فقط.",
            )
        if best_score.score >= 70:
            return CertificationPreparation(
                "تحتاج بيانات إضافية",
                "النتيجة مقبولة بحثيا لكن تحتاج عينة أوسع.",
            )
        if best_score.score >= 55:
            return CertificationPreparation(
                "تحتاج تحسين",
                "يلزم تحسين الجودة أو الاستقرار قبل المقارنة المتقدمة.",
            )
        return CertificationPreparation(
            "غير مؤهلة",
            "النتيجة البحثية غير كافية ولا تمثل توصية تداول.",
        )
