"""Diagnostics and recommendations for broker observation readiness."""

from __future__ import annotations

from app.broker_readiness.models import BrokerRecommendation, DiagnosticFinding
from app.broker_readiness.models import ReadinessScore, RestrictionReport
from app.broker_readiness.models import ValidationResult


class BrokerReadinessDiagnostics:
    """Detect weak passive observation readiness areas."""

    def evaluate(
        self,
        readiness: ReadinessScore,
        validation: ValidationResult,
        restrictions: RestrictionReport,
    ) -> tuple[DiagnosticFinding, ...]:
        checks = {
            "ضعف تغطية المراقبة": readiness.observation_readiness,
            "ضعف المراقبة": readiness.monitoring_readiness,
            "ضعف التشخيص": validation.observation_diagnostics,
            "ضعف الجاهزية": readiness.score,
            "إخفاق القيود": readiness.restriction_compliance,
        }
        findings = []
        for name, value in checks.items():
            if value >= 70:
                continue
            severity = "مرتفع" if value < 45 else "متوسط" if value < 60 else "منخفض"
            findings.append(
                DiagnosticFinding(name, severity, f"{name}: الدرجة {round(value, 2)}.")
            )
        if restrictions.status != "PASS":
            findings.append(
                DiagnosticFinding("انتهاكات السلامة", "مرتفع", "فشل قيود السلامة.")
            )
        return tuple(findings)


class BrokerReadinessRecommendationEngine:
    """Generate Arabic passive-readiness recommendations."""

    MAP = {
        "ضعف تغطية المراقبة": "تحسين تغطية المراقبة",
        "ضعف التشخيص": "تحسين التشخيص",
        "ضعف المراقبة": "تحسين التحقق",
        "ضعف الجاهزية": "تحسين التقارير",
        "إخفاق القيود": "تحسين العزل الأمني",
        "انتهاكات السلامة": "تحسين العزل الأمني",
    }

    def generate(
        self,
        diagnostics: tuple[DiagnosticFinding, ...],
    ) -> tuple[BrokerRecommendation, ...]:
        if not diagnostics:
            return (
                BrokerRecommendation(
                    "المتابعة السلبية المستمرة",
                    "منخفضة",
                    "لا توجد عوائق رئيسية في جاهزية المراقبة السلبية.",
                ),
            )
        return tuple(
            BrokerRecommendation(
                self.MAP.get(item.name, "تحسين التحقق"),
                "عالية" if item.severity == "مرتفع" else "متوسطة",
                item.detail,
            )
            for item in diagnostics
        )
