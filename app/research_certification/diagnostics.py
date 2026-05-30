"""Certification diagnostics."""

from __future__ import annotations

from app.research_certification.models import DiagnosticFinding


class CertificationDiagnosticsEngine:
    """Detect certification weaknesses with Arabic severity labels."""

    CHECKS = (
        ("ضعف الجاهزية", "readiness_score", 55),
        ("ضعف المتانة", "robustness_score", 55),
        ("ضعف الاتساق", "consistency_score", 55),
        ("ضعف الثبات", "stability_score", 55),
        ("ضعف أداء المعيار", "benchmark_score", 55),
        ("حجم عينة غير كاف", "sample_size", 20),
        ("ضعف جودة الأنماط", "pattern_quality", 55),
        ("ضعف التكيف مع حالة السوق", "regime_score", 55),
    )

    def evaluate(self, values: dict[str, float]) -> tuple[DiagnosticFinding, ...]:
        findings = []
        for name, key, threshold in self.CHECKS:
            value = float(values.get(key, 0))
            if value >= threshold:
                continue
            severity = "مرتفع" if value < threshold * 0.6 else "متوسط"
            if value >= threshold * 0.8:
                severity = "منخفض"
            findings.append(
                DiagnosticFinding(
                    name,
                    severity,
                    f"{name}: القيمة {round(value, 2)} أقل من الحد {threshold}.",
                )
            )
        return tuple(findings)
