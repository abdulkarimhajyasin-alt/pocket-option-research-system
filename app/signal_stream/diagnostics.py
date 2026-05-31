"""Diagnostics and recommendations for signal stream."""

from __future__ import annotations

from app.signal_stream.models import SignalDiagnostic
from app.signal_stream.models import SignalDirection
from app.signal_stream.models import SignalEvent
from app.signal_stream.models import SignalRecommendation
from app.signal_stream.models import SignalScoreResult
from app.signal_stream.models import SignalValidationResult


class SignalStreamDiagnostics:
    """Detect signal conflicts, duplicates, instability, low confidence, weak observations."""

    def evaluate(
        self,
        events: tuple[SignalEvent, ...],
        scoring: SignalScoreResult,
        validation: SignalValidationResult,
    ) -> tuple[SignalDiagnostic, ...]:
        findings: list[SignalDiagnostic] = []
        if any(item.direction == SignalDirection.NO_TRADE for item in events):
            findings.append(
                SignalDiagnostic("إشارات ضعيفة", "متوسط", "توجد إشارات مصنفة للبحث فقط كعدم تداول.")
            )
        if len({item.signal_id for item in events}) != len(events):
            findings.append(
                SignalDiagnostic("إشارات مكررة", "مرتفع", "توجد معرفات إشارات مكررة.")
            )
        if scoring.stream_stability < 70:
            findings.append(
                SignalDiagnostic("تدفق غير مستقر", "متوسط", "كثافة التدفق أقل من المستوى المطلوب.")
            )
        if scoring.confidence_quality < 60:
            findings.append(
                SignalDiagnostic("ثقة منخفضة", "متوسط", "متوسط الثقة في الإشارات منخفض.")
            )
        if validation.score < 80:
            findings.append(
                SignalDiagnostic("ملاحظات ضعيفة", "منخفض", "مصادر الملاحظات تحتاج تقوية.")
            )
        if not findings:
            findings.append(
                SignalDiagnostic("استقرار تدفق الإشارات", "منخفض", "تدفق الإشارات مستقر للبحث.")
            )
        return tuple(findings)


class SignalStreamRecommendationEngine:
    """Generate Arabic signal stream recommendations."""

    mapping = {
        "إشارات ضعيفة": "تحسين الجودة",
        "إشارات مكررة": "تحسين الاتساق",
        "تدفق غير مستقر": "تحسين الاستقرار",
        "ثقة منخفضة": "تحسين الثقة",
        "ملاحظات ضعيفة": "تحسين التغطية",
        "استقرار تدفق الإشارات": "تحسين الجاهزية",
    }

    def generate(
        self,
        diagnostics: tuple[SignalDiagnostic, ...],
    ) -> tuple[SignalRecommendation, ...]:
        return tuple(
            SignalRecommendation(
                title=self.mapping.get(item.name, "تحسين الجودة"),
                priority=item.severity,
                reason=item.detail,
            )
            for item in diagnostics
        )
