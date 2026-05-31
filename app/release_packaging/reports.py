"""Report writer for release packaging."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ReleasePackagingReportWriter:
    """Write release packaging reports."""

    def __init__(self, output_dir: Path | str = "reports/release_packaging") -> None:
        self.output_dir = Path(output_dir)

    def export(
        self,
        manifest: dict[str, Any],
        status: dict[str, Any],
        notes: dict[str, Any],
        audit: dict[str, Any],
        diagnostics: list[dict[str, Any]],
        recommendations: list[str],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        summary = {
            "release_id": manifest.get("release_id"),
            "release_status": manifest.get("release_status"),
            "certification_state": manifest.get("certification_state"),
            "test_count": manifest.get("test_count"),
            "recommended_next_decision": status.get("recommended_next_decision"),
            "research_only": True,
        }
        paths = {
            "summary": self.output_dir / "release_summary.json",
            "notes": self.output_dir / "release_notes.json",
            "status": self.output_dir / "project_status_report.json",
            "architecture": self.output_dir / "architecture_summary.json",
            "audit": self.output_dir / "repository_audit_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
            "manifest": self.output_dir / "release_manifest_report.json",
        }
        self._write(paths["summary"], summary)
        self._write(paths["notes"], notes)
        self._write(paths["status"], status)
        self._write(paths["architecture"], self._architecture_summary(audit))
        self._write(paths["audit"], audit)
        self._write(paths["diagnostics"], diagnostics)
        self._write(paths["recommendations"], recommendations)
        self._write(paths["manifest"], manifest)
        return {key: str(path) for key, path in paths.items()}

    def _architecture_summary(self, audit: dict[str, Any]) -> dict[str, Any]:
        return {
            "module_count": len(audit.get("module_inventory", [])),
            "dashboard_route_count": len(audit.get("dashboard_route_inventory", [])),
            "api_endpoint_count": len(audit.get("api_endpoint_inventory", [])),
            "script_count": len(audit.get("script_inventory", [])),
            "test_count": len(audit.get("test_inventory", [])),
            "research_only": True,
        }

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
