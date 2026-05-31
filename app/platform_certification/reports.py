"""Report writer for platform certification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.platform_certification.models import PlatformCertificationResult


class PlatformCertificationReportWriter:
    """Write dashboard-ready certification reports."""

    def __init__(self, output_dir: Path | str = "reports/platform_certification") -> None:
        self.output_dir = Path(output_dir)

    def export(self, result: PlatformCertificationResult) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        executive = {
            "final_platform_score": payload["final_platform_score"],
            "certification_state": payload["certification_state"],
            "research_maturity_level": payload["research_maturity_level"],
            "maturity_score": payload["maturity_score"],
            "research_only": True,
            "local_only": True,
        }
        paths = {
            "certification": self.output_dir / "certification_report.json",
            "executive": self.output_dir / "executive_summary.json",
            "domains": self.output_dir / "domain_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(paths["certification"], payload)
        self._write(paths["executive"], executive)
        self._write(paths["domains"], payload["domain_scores"])
        self._write(paths["diagnostics"], payload["diagnostics"])
        self._write(paths["recommendations"], payload["recommendations"])
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
