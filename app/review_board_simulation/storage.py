"""Storage writer for review board simulation outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ReviewBoardSimulationStorage:
    """Write simulation artifacts to local storage."""

    MAPPING = {
        "source_inventory": "source_inventory.json",
        "board_registry": "board_registry.json",
        "board_simulation_results": "board_simulation_results.json",
        "gate_dry_run_results": "gate_dry_run_results.json",
        "evidence_review": "evidence_review.json",
        "blocker_analysis": "blocker_analysis.json",
        "decision_scores": "decision_scores.json",
        "findings": "findings.json",
        "readiness_summary": "readiness_summary.json",
        "diagnostics": "diagnostics.json",
        "recommendations": "recommendations.json",
        "summary": "summary.json",
    }

    def __init__(self, output_dir: Path | str = "storage/review_board_simulation") -> None:
        self.output_dir = Path(output_dir)

    def save(self, payloads: dict[str, Any]) -> dict[str, str]:
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
