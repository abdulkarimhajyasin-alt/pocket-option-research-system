"""Diagnostics and recommendations for manual snapshot imports."""

from __future__ import annotations

from app.snapshot_import.models import QualityResult
from app.snapshot_import.models import SafetyStatus
from app.snapshot_import.models import SnapshotDiagnostic
from app.snapshot_import.models import SnapshotImport
from app.snapshot_import.models import SnapshotRecommendation
from app.snapshot_import.models import ValidationResult


class SnapshotDiagnosticsEngine:
    """Detect invalid, corrupted, incomplete, stale, and weak visibility imports."""

    def evaluate(
        self,
        imports: tuple[SnapshotImport, ...],
        validation: ValidationResult,
        quality: QualityResult,
        safety: SafetyStatus,
    ) -> tuple[SnapshotDiagnostic, ...]:
        findings: list[SnapshotDiagnostic] = []
        invalid = [item for item in imports if item.validation_status != "ناجح"]
        corrupted = [item for item in imports if not item.metadata.get("readable")]
        incomplete = [item for item in imports if item.size_bytes == 0]
        stale = [item for item in imports if item.imported_at == "0"]
        if invalid:
            findings.append(
                SnapshotDiagnostic(
                    "استيرادات غير صالحة",
                    "متوسط",
                    f"عدد الملفات التي تحتاج مراجعة: {len(invalid)}",
                )
            )
        if corrupted:
            findings.append(
                SnapshotDiagnostic(
                    "ملفات تالفة",
                    "مرتفع",
                    f"عدد الملفات غير القابلة للقراءة: {len(corrupted)}",
                )
            )
        if incomplete:
            findings.append(
                SnapshotDiagnostic(
                    "ملفات غير مكتملة",
                    "متوسط",
                    f"عدد الملفات الفارغة: {len(incomplete)}",
                )
            )
        if stale:
            findings.append(
                SnapshotDiagnostic(
                    "لقطات قديمة",
                    "منخفض",
                    f"عدد اللقطات دون وقت صالح: {len(stale)}",
                )
            )
        if quality.visibility < 70:
            findings.append(
                SnapshotDiagnostic(
                    "رؤية ضعيفة",
                    "متوسط",
                    "وضوح المعلومات المرئية أقل من المستوى المطلوب.",
                )
            )
        if validation.score < 70 or safety.status != "PASS":
            findings.append(
                SnapshotDiagnostic(
                    "رفض محتمل",
                    "مرتفع",
                    "التحقق أو السلامة لا يكفيان لقبول الاستيراد.",
                )
            )
        return tuple(findings)


class SnapshotRecommendationEngine:
    """Generate Arabic recommendations from snapshot diagnostics."""

    def generate(
        self,
        diagnostics: tuple[SnapshotDiagnostic, ...],
    ) -> tuple[SnapshotRecommendation, ...]:
        mapping = {
            "استيرادات غير صالحة": "تحسين جودة اللقطة",
            "ملفات تالفة": "إعادة إنشاء اللقطة",
            "ملفات غير مكتملة": "تحسين اكتمال البيانات",
            "لقطات قديمة": "تحديث البيانات",
            "رؤية ضعيفة": "تحسين وضوح المصدر",
            "رفض محتمل": "تحسين التحقق",
        }
        recommendations = [
            SnapshotRecommendation(
                mapping.get(item.name, "تحسين جودة اللقطة"),
                item.severity,
                item.detail,
            )
            for item in diagnostics
        ]
        if not recommendations:
            recommendations.append(
                SnapshotRecommendation(
                    "متابعة الاستيراد اليدوي",
                    "منخفض",
                    "الملفات صالحة للتحليل ضمن حدود القراءة فقط.",
                )
            )
        return tuple(recommendations)
