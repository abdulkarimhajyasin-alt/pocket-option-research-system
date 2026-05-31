"""Diagnostics for release packaging."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.release_packaging.schemas import FORBIDDEN_RELEASE_STATUSES, RELEASE_ID


class ReleasePackagingDiagnostics:
    """Detect release packaging readiness issues."""

    PHASE_OUTPUTS = {
        "phase_50": ("reports", "architecture_audit", "architecture_summary.json"),
        "phase_51": ("reports", "knowledge_graph", "knowledge_summary.json"),
        "phase_52": ("reports", "research_api", "research_summary.json"),
        "phase_53": ("reports", "research_archive", "archive_summary.json"),
        "phase_54": ("reports", "platform_certification", "certification_report.json"),
    }

    def evaluate(
        self,
        root: Path,
        audit: dict[str, Any],
        manifest: dict[str, Any] | None = None,
        status: dict[str, Any] | None = None,
        notes: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        diagnostics: list[dict[str, Any]] = []
        for phase, parts in self.PHASE_OUTPUTS.items():
            if not root.joinpath(*parts).exists():
                self._add(diagnostics, f"missing_{phase}_outputs", "مرتفع")
        if manifest is not None:
            self._manifest(diagnostics, manifest)
        if status is not None and not status:
            self._add(diagnostics, "missing_project_status", "متوسط")
        if notes is not None and not notes:
            self._add(diagnostics, "missing_release_notes", "متوسط")
        if audit.get("invalid_json_files"):
            self._add(diagnostics, "invalid_json_report_files", "مرتفع")
        if audit.get("missing_expected", {}).get("dashboard_templates"):
            self._add(diagnostics, "incomplete_dashboard_integration", "متوسط")
        if audit.get("missing_expected", {}).get("arabic_labels"):
            self._add(diagnostics, "incomplete_api_integration", "متوسط")
        if audit.get("unsafe_module_terms"):
            self._add(diagnostics, "forbidden_capability_wording", "مرتفع")
        return diagnostics

    def _manifest(self, diagnostics: list[dict[str, Any]], manifest: dict[str, Any]) -> None:
        if manifest.get("release_id") != RELEASE_ID:
            self._add(diagnostics, "invalid_release_manifest", "مرتفع")
        if manifest.get("release_status") in FORBIDDEN_RELEASE_STATUSES:
            self._add(diagnostics, "unsafe_release_state_wording", "مرتفع")
        if not manifest.get("safety_boundary"):
            self._add(diagnostics, "missing_safety_boundary", "مرتفع")

    def validate_release_outputs(self, root: Path) -> list[dict[str, Any]]:
        diagnostics: list[dict[str, Any]] = []
        required = (
            ("storage", "release_packaging", "release_manifest.json"),
            ("storage", "release_packaging", "project_status.json"),
            ("reports", "release_packaging", "release_notes.json"),
        )
        for parts in required:
            path = root.joinpath(*parts)
            if not path.exists():
                self._add(diagnostics, "missing_release_outputs", "متوسط")
            elif not self._valid_json(path):
                self._add(diagnostics, "invalid_json_report_files", "مرتفع")
        return diagnostics

    def _add(self, diagnostics: list[dict[str, Any]], code: str, severity: str) -> None:
        diagnostics.append({"code": code, "severity": severity, "research_only": True})

    def _valid_json(self, path: Path) -> bool:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        return True
