"""Report writer for review board simulation outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ReviewBoardSimulationReportWriter:
    """Write simulation report artifacts."""

    MAPPING = {
        "summary": "review_board_simulation_summary.json",
        "source_inventory": "source_inventory_report.json",
        "board_registry": "board_registry_report.json",
        "board_simulation_results": "board_simulation_report.json",
        "gate_dry_run_results": "gate_dry_run_report.json",
        "evidence_review": "evidence_review_report.json",
        "blocker_analysis": "blocker_analysis_report.json",
        "decision_scores": "decision_scores_report.json",
        "findings": "findings_report.json",
        "readiness_summary": "readiness_report.json",
        "diagnostics": "diagnostics_report.json",
        "recommendations": "recommendations_report.json",
    }

    def __init__(self, output_dir: Path | str = "reports/review_board_simulation") -> None:
        self.output_dir = Path(output_dir)

    def export(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {}
        for key, filename in self.MAPPING.items():
            path = self.output_dir / filename
            path.write_text(
                json.dumps(payloads.get(key, {}), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            paths[key] = str(path)
        return paths
