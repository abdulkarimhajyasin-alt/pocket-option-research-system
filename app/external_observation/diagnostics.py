"""Diagnostics and recommendations for external observation sandbox."""

from __future__ import annotations

from app.external_observation.models import HealthResult
from app.external_observation.models import IsolationStatus
from app.external_observation.models import MonitoringResult
from app.external_observation.models import ObservationDiagnostic
from app.external_observation.models import ObservationRecommendation
from app.external_observation.models import ObservationSource
from app.external_observation.models import SourceValidationResult


class ObservationDiagnosticsEngine:
    """Detect invalid, incomplete, unstable, weak coverage, and isolation issues."""

    def evaluate(
        self,
        sources: tuple[ObservationSource, ...],
        validation: SourceValidationResult,
        monitoring: MonitoringResult,
        isolation: IsolationStatus,
        health: HealthResult,
    ) -> tuple[ObservationDiagnostic, ...]:
        findings: list[ObservationDiagnostic] = []
        invalid = [item for item in sources if item.validation_status != "ناجح"]
        incomplete = [item for item in sources if item.observation_status != "نشط"]
        if invalid:
            findings.append(
                ObservationDiagnostic(
                    "مصادر غير صالحة",
                    "متوسط",
                    f"عدد المصادر التي تحتاج تحقق إضافي: {len(invalid)}",
                )
            )
        if incomplete:
            findings.append(
                ObservationDiagnostic(
                    "مصادر غير مكتملة",
                    "متوسط",
                    f"عدد المصادر غير المكتملة: {len(incomplete)}",
                )
            )
        if monitoring.stability < 75:
            findings.append(
                ObservationDiagnostic(
                    "استقرار ضعيف",
                    "منخفض",
                    "استقرار المصادر أقل من المستوى المستهدف.",
                )
            )
        if monitoring.coverage < 80:
            findings.append(
                ObservationDiagnostic(
                    "تغطية ضعيفة",
                    "متوسط",
                    "تغطية المصادر تحتاج توسعا قبل المراقبة المتقدمة.",
                )
            )
        if validation.score < 70 or health.score < 70:
            findings.append(
                ObservationDiagnostic(
                    "صحة غير كافية",
                    "مرتفع",
                    "صحة الصندوق لا تكفي لتوسيع مصادر المراقبة.",
                )
            )
        if isolation.status != "PASS":
            findings.append(
                ObservationDiagnostic(
                    "مشكلة عزل",
                    "مرتفع",
                    "العزل يجب أن يبقى ناجحا قبل أي توسع بحثي.",
                )
            )
        return tuple(findings)


class ObservationRecommendationEngine:
    """Generate Arabic recommendations from diagnostics."""

    def generate(
        self,
        diagnostics: tuple[ObservationDiagnostic, ...],
    ) -> tuple[ObservationRecommendation, ...]:
        mapping = {
            "مصادر غير صالحة": "تحسين جودة المصدر",
            "مصادر غير مكتملة": "تحسين التغطية",
            "استقرار ضعيف": "تحسين الاستقرار",
            "تغطية ضعيفة": "تحسين التغطية",
            "صحة غير كافية": "تحسين التحقق",
            "مشكلة عزل": "تحسين العزل",
        }
        recommendations = [
            ObservationRecommendation(
                title=mapping.get(item.name, "تحسين جودة المصدر"),
                priority=item.severity,
                reason=item.detail,
            )
            for item in diagnostics
        ]
        if not recommendations:
            recommendations.append(
                ObservationRecommendation(
                    "متابعة المراقبة السلبية",
                    "منخفض",
                    "الصندوق يعمل ضمن حدود البحث والمراقبة فقط.",
                )
            )
        return tuple(recommendations)
