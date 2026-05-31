"""Diagnostics and recommendations for browser observation artifacts."""

from __future__ import annotations

from app.browser_observation.models import BrowserObservationDiagnostic
from app.browser_observation.models import BrowserObservationRecommendation
from app.browser_observation.models import MonitoringResult
from app.browser_observation.models import ObservationArtifact
from app.browser_observation.models import SafetyStatus
from app.browser_observation.models import ValidationResult
from app.browser_observation.models import VisibilityResult


class BrowserObservationDiagnostics:
    """Detect invalid, incomplete, missing, low quality, and stale artifacts."""

    def evaluate(
        self,
        artifacts: tuple[ObservationArtifact, ...],
        validation: ValidationResult,
        visibility: VisibilityResult,
        monitoring: MonitoringResult,
        safety: SafetyStatus,
    ) -> tuple[BrowserObservationDiagnostic, ...]:
        findings: list[BrowserObservationDiagnostic] = []
        invalid = [item for item in artifacts if item.validation_status != "ناجح"]
        incomplete = [item for item in artifacts if item.visibility_status != "مرئي"]
        stale = [item for item in artifacts if item.created_at == "0"]
        if invalid:
            findings.append(
                BrowserObservationDiagnostic(
                    "لقطات غير صالحة",
                    "متوسط",
                    f"عدد اللقطات التي تحتاج تحقق إضافي: {len(invalid)}",
                )
            )
        if incomplete:
            findings.append(
                BrowserObservationDiagnostic(
                    "لقطات غير مكتملة",
                    "متوسط",
                    f"عدد اللقطات ذات الرؤية الناقصة: {len(incomplete)}",
                )
            )
        if visibility.score < 75:
            findings.append(
                BrowserObservationDiagnostic(
                    "رؤية ناقصة",
                    "متوسط",
                    "درجة الرؤية أقل من المستوى المستهدف.",
                )
            )
        if monitoring.quality < 75 or validation.score < 75:
            findings.append(
                BrowserObservationDiagnostic(
                    "جودة منخفضة",
                    "مرتفع",
                    "جودة اللقطات أو تحققها يحتاج تحسين.",
                )
            )
        if stale:
            findings.append(
                BrowserObservationDiagnostic(
                    "لقطات قديمة",
                    "منخفض",
                    f"عدد اللقطات التي لا تحمل وقتا صالحا: {len(stale)}",
                )
            )
        if safety.status != "PASS":
            findings.append(
                BrowserObservationDiagnostic(
                    "خلل سلامة",
                    "مرتفع",
                    "السلامة يجب أن تبقى للقراءة فقط دون تحكم.",
                )
            )
        return tuple(findings)


class BrowserObservationRecommendationEngine:
    """Generate Arabic recommendations from diagnostics."""

    def generate(
        self,
        diagnostics: tuple[BrowserObservationDiagnostic, ...],
    ) -> tuple[BrowserObservationRecommendation, ...]:
        mapping = {
            "لقطات غير صالحة": "تحسين جودة اللقطة",
            "لقطات غير مكتملة": "تحسين اكتمال البيانات",
            "رؤية ناقصة": "تحسين الرؤية",
            "جودة منخفضة": "تحسين التحقق",
            "لقطات قديمة": "تحسين التغطية",
            "خلل سلامة": "تحسين التحقق",
        }
        recommendations = [
            BrowserObservationRecommendation(
                mapping.get(item.name, "تحسين جودة اللقطة"),
                item.severity,
                item.detail,
            )
            for item in diagnostics
        ]
        if not recommendations:
            recommendations.append(
                BrowserObservationRecommendation(
                    "متابعة المراقبة للقراءة فقط",
                    "منخفض",
                    "اللقطات صالحة ضمن حدود القراءة والتحليل فقط.",
                )
            )
        return tuple(recommendations)
