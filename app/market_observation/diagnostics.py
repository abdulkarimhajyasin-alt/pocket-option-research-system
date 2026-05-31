"""Diagnostics for canonical market observation."""

from __future__ import annotations

from app.market_observation.models import MarketObservationAggregate
from app.market_observation.models import MarketObservationDiagnostic
from app.market_observation.models import MarketObservationValidation


class MarketObservationDiagnosticsEngine:
    """Generate Arabic diagnostics for weak observation dimensions."""

    def evaluate(
        self,
        validation: MarketObservationValidation,
        aggregate: MarketObservationAggregate,
    ) -> tuple[MarketObservationDiagnostic, ...]:
        findings: list[MarketObservationDiagnostic] = []
        if validation.completeness < 85:
            findings.append(
                MarketObservationDiagnostic(
                    "تغطية المصادر",
                    "warning",
                    "بعض مصادر المراقبة السلبية غير متاحة في المصدر الموحد.",
                )
            )
        if aggregate.quality_score < 75:
            findings.append(
                MarketObservationDiagnostic(
                    "جودة الملاحظة",
                    "warning",
                    "جودة المخرجات تحتاج تحسين قبل الاعتماد البحثي الكامل.",
                )
            )
        if aggregate.confidence_score < 75:
            findings.append(
                MarketObservationDiagnostic(
                    "ثقة الملاحظة",
                    "warning",
                    "درجة الثقة أقل من مستوى الاعتماد المفضل.",
                )
            )
        if not findings:
            findings.append(
                MarketObservationDiagnostic(
                    "حالة المصدر الموحد",
                    "healthy",
                    "مصدر مراقبة السوق الموحد جاهز للاستخدام البحثي.",
                )
            )
        return tuple(findings)
