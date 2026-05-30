"""Certification requirements engine."""

from __future__ import annotations

from app.research_certification.models import RequirementCheck, RequirementsReport
from app.research_certification.scoring import clamp


DEFAULT_THRESHOLDS = {
    "minimum_sample_size": 20,
    "minimum_readiness_score": 55,
    "minimum_stability_score": 55,
    "minimum_consistency_score": 55,
    "minimum_robustness_score": 55,
    "minimum_benchmark_score": 55,
    "minimum_lifecycle_quality": 55,
}


class CertificationRequirementsEngine:
    """Evaluate configurable certification requirements."""

    def __init__(self, thresholds: dict[str, float] | None = None) -> None:
        self.thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    def evaluate(
        self,
        inputs: dict[str, float],
        robustness_score: float,
        consistency_score: float,
        stability_score: float,
    ) -> RequirementsReport:
        checks = (
            self._check("حجم العينة", inputs.get("sample_size", 0), "minimum_sample_size"),
            self._check("الجاهزية", inputs.get("readiness_score", 0), "minimum_readiness_score"),
            self._check("الثبات", stability_score, "minimum_stability_score"),
            self._check("الاتساق", consistency_score, "minimum_consistency_score"),
            self._check("المتانة", robustness_score, "minimum_robustness_score"),
            self._check("المعيار", inputs.get("benchmark_score", 0), "minimum_benchmark_score"),
            self._check(
                "جودة دورة الحياة",
                inputs.get("lifecycle_quality", 0),
                "minimum_lifecycle_quality",
            ),
        )
        failures = sum(1 for item in checks if item.status == "FAIL")
        warnings = sum(1 for item in checks if item.status == "WARNING")
        return RequirementsReport(checks, failures == 0, warnings, failures)

    def _check(self, name: str, value: float, threshold_key: str) -> RequirementCheck:
        threshold = self.thresholds[threshold_key]
        status = "PASS" if value >= threshold else "WARNING" if value >= threshold * 0.8 else "FAIL"
        status_ar = {"PASS": "ناجح", "WARNING": "تحذير", "FAIL": "فشل"}[status]
        explanation = f"{name}: {clamp(value)} مقابل حد {threshold}."
        return RequirementCheck(name, clamp(value), threshold, status, status_ar, explanation)
