"""Report writer for post-research strategic architecture outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PostResearchArchitectureReportWriter:
    """Write post-research architecture report artifacts."""

    def __init__(self, output_dir: Path | str = "reports/post_research_architecture") -> None:
        self.output_dir = Path(output_dir)

    def export(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "summary": "post_research_summary.json",
            "roadmap": "roadmap_report.json",
            "gap_analysis": "gap_analysis_report.json",
            "execution_blueprint": "execution_blueprint_report.json",
            "broker_blueprint": "broker_blueprint_report.json",
            "risk_blueprint": "risk_blueprint_report.json",
            "monitoring_blueprint": "monitoring_blueprint_report.json",
            "governance_blueprint": "governance_blueprint_report.json",
            "transition_plan": "transition_plan_report.json",
            "diagnostics": "diagnostics_report.json",
            "recommendations": "recommendations_report.json",
        }
        paths = {}
        for key, filename in mapping.items():
            path = self.output_dir / filename
            self._write(path, payloads.get(key, {}))
            paths[key] = str(path)
        return paths

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
