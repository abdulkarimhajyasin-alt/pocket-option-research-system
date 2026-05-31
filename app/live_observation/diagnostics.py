"""Diagnostics and recommendations for live observation replay."""

from __future__ import annotations

from app.live_observation.models import LiveObservation
from app.live_observation.models import ReplayDiagnostic
from app.live_observation.models import ReplayQualityResult
from app.live_observation.models import ReplayRecommendation
from app.live_observation.models import ReplayReadinessResult
from app.live_observation.models import ReplayValidationResult
from app.live_observation.models import TimelineResult


class ReplayDiagnosticsEngine:
    """Detect missing observations, sequence issues, gaps, conflicts, and staleness."""

    def evaluate(
        self,
        observations: tuple[LiveObservation, ...],
        timeline: TimelineResult,
        quality: ReplayQualityResult,
        readiness: ReplayReadinessResult,
        validation: ReplayValidationResult,
    ) -> tuple[ReplayDiagnostic, ...]:
        findings: list[ReplayDiagnostic] = []
        if len(observations) < 5:
            findings.append(
                ReplayDiagnostic(
                    "ملاحظات مفقودة",
                    "مرتفع",
                    "عدد الملاحظات لا يكفي لإعادة تشغيل مستقرة.",
                )
            )
        if validation.sequence_integrity < 100:
            findings.append(
                ReplayDiagnostic(
                    "تسلسل غير صالح",
                    "مرتفع",
                    "تسلسل الأحداث يحتاج مراجعة.",
                )
            )
        if timeline.coverage < 80:
            findings.append(
                ReplayDiagnostic(
                    "فجوات زمنية",
                    "متوسط",
                    "تغطية الخط الزمني أقل من المستوى المطلوب.",
                )
            )
        if validation.replay_consistency < 100:
            findings.append(
                ReplayDiagnostic(
                    "تعارض إعادة التشغيل",
                    "متوسط",
                    "توجد معرفات مكررة أو تعارض في الملاحظات.",
                )
            )
        if quality.stability < 75 or readiness.score < 75:
            findings.append(
                ReplayDiagnostic(
                    "ملاحظات قديمة",
                    "منخفض",
                    "استقرار أو جاهزية إعادة التشغيل يحتاج متابعة.",
                )
            )
        if not findings:
            findings.append(
                ReplayDiagnostic(
                    "استقرار إعادة التشغيل",
                    "منخفض",
                    "إعادة التشغيل مستقرة للاستخدام البحثي.",
                )
            )
        return tuple(findings)


class ReplayRecommendationEngine:
    """Generate Arabic replay recommendations."""

    titles = {
        "ملاحظات مفقودة": "تحسين التغطية",
        "تسلسل غير صالح": "تحسين التسلسل",
        "فجوات زمنية": "تحسين الاتساق",
        "تعارض إعادة التشغيل": "تحسين التحقق",
        "ملاحظات قديمة": "تحسين الجاهزية",
        "استقرار إعادة التشغيل": "تحسين الجودة",
    }

    def generate(
        self,
        diagnostics: tuple[ReplayDiagnostic, ...],
    ) -> tuple[ReplayRecommendation, ...]:
        recommendations = [
            ReplayRecommendation(
                title=self.titles.get(item.name, "تحسين الجودة"),
                priority=item.severity,
                reason=item.detail,
            )
            for item in diagnostics
        ]
        return tuple(recommendations)
