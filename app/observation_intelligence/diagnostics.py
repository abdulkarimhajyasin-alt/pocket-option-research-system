"""Diagnostics and recommendations for unified observation intelligence."""

from __future__ import annotations

from app.observation_intelligence.models import AggregationResult
from app.observation_intelligence.models import ConfidenceResult
from app.observation_intelligence.models import ObservationDiagnostic
from app.observation_intelligence.models import ObservationRecommendation
from app.observation_intelligence.models import QualityResult
from app.observation_intelligence.models import UnifiedObservation


class ObservationDiagnosticsEngine:
    """Detect incomplete, conflicting, stale, low confidence, and weak coverage."""

    def evaluate(
        self,
        observations: tuple[UnifiedObservation, ...],
        aggregation: AggregationResult,
        confidence: ConfidenceResult,
        quality: QualityResult,
    ) -> tuple[ObservationDiagnostic, ...]:
        findings: list[ObservationDiagnostic] = []
        incomplete = [item for item in observations if item.quality_score < 70]
        stale = [item for item in observations if not item.timestamp]
        low_confidence = [item for item in observations if item.confidence_score < 70]
        if incomplete:
            findings.append(
                ObservationDiagnostic(
                    "ملاحظات غير مكتملة",
                    "متوسط",
                    f"عدد الملاحظات ذات الجودة الضعيفة: {len(incomplete)}",
                )
            )
        if aggregation.conflicts:
            findings.append(
                ObservationDiagnostic(
                    "تضارب الملاحظات",
                    "مرتفع",
                    f"عدد مصادر التضارب: {int(aggregation.conflicts)}",
                )
            )
        if stale:
            findings.append(
                ObservationDiagnostic(
                    "ملاحظات قديمة",
                    "منخفض",
                    f"عدد الملاحظات دون وقت صالح: {len(stale)}",
                )
            )
        if low_confidence or confidence.score < 75:
            findings.append(
                ObservationDiagnostic(
                    "ثقة منخفضة",
                    "متوسط",
                    "درجة الثقة الموحدة أقل من المستوى المستهدف.",
                )
            )
        if aggregation.coverage < 80 or quality.completeness < 60:
            findings.append(
                ObservationDiagnostic(
                    "تغطية ضعيفة",
                    "متوسط",
                    "التغطية أو الاكتمال يحتاجان تحسين.",
                )
            )
        return tuple(findings)


class ObservationRecommendationEngine:
    """Generate Arabic observation intelligence recommendations."""

    def generate(
        self,
        diagnostics: tuple[ObservationDiagnostic, ...],
    ) -> tuple[ObservationRecommendation, ...]:
        mapping = {
            "ملاحظات غير مكتملة": "تحسين الجودة",
            "تضارب الملاحظات": "تحسين الاتساق",
            "ملاحظات قديمة": "تحسين التغطية",
            "ثقة منخفضة": "تحسين الثقة",
            "تغطية ضعيفة": "تحسين الرؤية",
        }
        recommendations = [
            ObservationRecommendation(
                mapping.get(item.name, "تحسين التغطية"),
                item.severity,
                item.detail,
            )
            for item in diagnostics
        ]
        if not recommendations:
            recommendations.append(
                ObservationRecommendation(
                    "متابعة ذكاء المراقبة",
                    "منخفض",
                    "النموذج الموحد صالح للتحليل البحثي.",
                )
            )
        return tuple(recommendations)
