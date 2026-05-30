"""Deterministic research certification reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ResearchCertificationReportWriter:
    """Write certification reports for dashboard and audit use."""

    def __init__(
        self,
        output_dir: Path | str = "reports/research_certification",
    ) -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "certification_summary.json",
            "requirements": self.output_dir / "requirements_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
            "maturity": self.output_dir / "maturity_report.json",
            "robustness": self.output_dir / "robustness_report.json",
            "consistency": self.output_dir / "consistency_report.json",
            "stability": self.output_dir / "stability_report.json",
        }
        self._write(
            paths["summary"],
            {
                "summary": analytics.get("summary", {}),
                "certification_distribution": analytics.get(
                    "certification_distribution",
                    {},
                ),
                "certification_timeline": analytics.get("certification_timeline", {}),
                "maturity_timeline": analytics.get("maturity_timeline", {}),
                "latest": analytics.get("latest", {}),
            },
        )
        self._write(paths["requirements"], analytics.get("requirements_distribution", {}))
        self._write(paths["diagnostics"], analytics.get("diagnostics_distribution", {}))
        self._write(
            paths["recommendations"],
            analytics.get("recommendation_distribution", {}),
        )
        self._write(paths["maturity"], analytics.get("maturity_distribution", {}))
        self._write(paths["robustness"], analytics.get("robustness_distribution", {}))
        self._write(paths["consistency"], analytics.get("consistency_distribution", {}))
        self._write(paths["stability"], analytics.get("stability_distribution", {}))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
