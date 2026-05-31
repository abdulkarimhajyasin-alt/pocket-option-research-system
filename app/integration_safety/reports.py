"""Report writer for integration safety boundary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.integration_safety.models import IntegrationSafetyRun


class IntegrationSafetyReportWriter:
    """Write integration safety reports."""

    def __init__(self, output_dir: Path | str = "reports/integration_safety") -> None:
        self.output_dir = Path(output_dir)

    def export(self, result: IntegrationSafetyRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "safety_summary.json",
            "boundary": self.output_dir / "boundary_report.json",
            "permissions": self.output_dir / "permission_report.json",
            "restrictions": self.output_dir / "restriction_report.json",
            "compliance": self.output_dir / "compliance_report.json",
            "audit": self.output_dir / "audit_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(
            paths["summary"],
            {"summary": result.policy.to_dict(), "latest": result.to_dict()},
        )
        self._write(paths["boundary"], result.boundary)
        self._write(paths["permissions"], result.permissions)
        self._write(paths["restrictions"], result.restrictions)
        self._write(paths["compliance"], result.compliance)
        self._write(paths["audit"], result.audit)
        self._write(paths["diagnostics"], self._count(item.name for item in result.diagnostics))
        self._write(
            paths["recommendations"],
            self._count(item.title for item in result.recommendations),
        )
        return {key: str(path) for key, path in paths.items()}

    def _count(self, values: Any) -> dict[str, int]:
        counts: dict[str, int] = {}
        for value in values:
            key = str(value)
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
