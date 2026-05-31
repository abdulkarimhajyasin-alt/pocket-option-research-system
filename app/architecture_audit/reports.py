"""Report writer for architecture audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.architecture_audit.models import ArchitectureAuditRun


class ArchitectureAuditReportWriter:
    """Write architecture audit reports."""

    def __init__(self, output_dir: Path | str = "reports/architecture_audit") -> None:
        self.output_dir = Path(output_dir)

    def export(self, result: ArchitectureAuditRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "architecture_summary.json",
            "consistency": self.output_dir / "consistency_report.json",
            "dependency": self.output_dir / "dependency_report.json",
            "performance": self.output_dir / "performance_report.json",
            "safety": self.output_dir / "safety_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
            "certification": self.output_dir / "final_certification.json",
        }
        self._write(
            paths["summary"],
            {"summary": result.certification.to_dict(), "latest": result.to_dict()},
        )
        self._write(paths["consistency"], result.consistency)
        self._write(paths["dependency"], result.dependency)
        self._write(paths["performance"], result.performance)
        self._write(paths["safety"], result.safety)
        self._write(paths["diagnostics"], self._count(item.name for item in result.diagnostics))
        self._write(
            paths["recommendations"],
            self._count(item.title for item in result.recommendations),
        )
        self._write(paths["certification"], result.certification.to_dict())
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
