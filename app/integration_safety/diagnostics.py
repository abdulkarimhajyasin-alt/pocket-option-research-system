"""Diagnostics for integration safety boundary."""

from __future__ import annotations

from typing import Any

from app.integration_safety.models import SafetyDiagnostic


class IntegrationSafetyDiagnostics:
    """Detect forbidden capability, metadata, wording, and audit risks."""

    def evaluate(
        self,
        permissions: dict[str, Any],
        restrictions: dict[str, Any],
        compliance: dict[str, Any],
        boundary: dict[str, Any],
        audit_present: bool,
    ) -> tuple[SafetyDiagnostic, ...]:
        diagnostics: list[SafetyDiagnostic] = []
        if restrictions.get("violations"):
            diagnostics.append(
                self._diag(
                    "خطر قدرة محظورة",
                    "مرتفع",
                    "توضيح القدرات المحظورة",
                )
            )
        if permissions.get("unknown_capabilities"):
            diagnostics.append(
                self._diag(
                    "قدرة غامضة",
                    "متوسط",
                    "توضيح القدرات المسموحة",
                )
            )
        if boundary.get("safety_score", 0) < 85:
            diagnostics.append(
                self._diag("حدود ضعيفة", "مرتفع", "تعزيز حدود الأمان")
            )
        if compliance.get("missing_flags"):
            diagnostics.append(
                self._diag(
                    "بيانات سلامة ناقصة",
                    "متوسط",
                    "تحسين بيانات السلامة",
                )
            )
        if not audit_present:
            diagnostics.append(
                self._diag(
                    "سجل تدقيق مفقود",
                    "منخفض",
                    "تحسين سجل التدقيق",
                )
            )
        if not diagnostics:
            diagnostics.append(
                self._diag(
                    "تحتاج طبقة العزل إلى مراجعة دورية",
                    "منخفض",
                    "تقوية طبقة العزل",
                )
            )
        return tuple(diagnostics)

    def _diag(self, name: str, severity: str, detail: str) -> SafetyDiagnostic:
        return SafetyDiagnostic(name=name, severity=severity, detail=detail)
