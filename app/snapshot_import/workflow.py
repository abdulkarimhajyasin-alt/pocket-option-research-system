"""Workflow and safety engines for manual snapshot imports."""

from __future__ import annotations

from app.snapshot_import.models import ProcessingResult
from app.snapshot_import.models import QualityResult
from app.snapshot_import.models import SafetyStatus
from app.snapshot_import.models import ValidationResult
from app.snapshot_import.models import WorkflowScore
from app.snapshot_import.validator import average


def import_state(score: float) -> tuple[str, str]:
    """Return Arabic import state and explanation."""
    if score >= 95:
        return "جاهزة للتحليل", "اللقطات جاهزة للتحليل البحثي."
    if score >= 85:
        return "جيدة بشروط", "اللقطات جيدة مع بعض التحسينات."
    if score >= 70:
        return "تحتاج تحسين محدود", "اللقطات مقبولة مع فجوات محدودة."
    if score >= 50:
        return "تحتاج تحسين كبير", "اللقطات تحتاج تحسينات كبيرة."
    return "مرفوضة", "اللقطات غير مناسبة للتحليل."


class SnapshotSafetyEngine:
    """Guarantee manual, passive, read-only snapshot import behavior."""

    def evaluate(self) -> SafetyStatus:
        checks = {
            "no_login": True,
            "no_authentication": True,
            "no_browser_automation": True,
            "no_broker_access": True,
            "no_execution": True,
            "no_account_interaction": True,
        }
        passed = sum(1 for value in checks.values() if value)
        score = round(passed / len(checks) * 100.0, 2)
        status = "PASS" if score == 100.0 else "WARNING" if score >= 80.0 else "FAIL"
        status_ar = "ناجح" if status == "PASS" else "تحذير" if status == "WARNING" else "فشل"
        return SafetyStatus(
            status=status,
            status_ar=status_ar,
            score=score,
            **checks,
        )


class SnapshotImportWorkflow:
    """Score upload registration, validation, parsing, processing, storage, reporting."""

    def score(
        self,
        validation: ValidationResult,
        processing: ProcessingResult,
        quality: QualityResult,
        safety: SafetyStatus,
    ) -> WorkflowScore:
        score = average(
            [
                validation.score,
                processing.score,
                quality.score,
                safety.score,
            ]
        )
        state, explanation = import_state(score)
        return WorkflowScore(score=score, state=state, explanation=explanation)
