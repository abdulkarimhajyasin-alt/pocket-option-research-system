"""Storage writer for post-research strategic architecture outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PostResearchArchitectureStorage:
    """Persist post-research architecture artifacts."""

    def __init__(self, output_dir: Path | str = "storage/post_research_architecture") -> None:
        self.output_dir = Path(output_dir)

    def save(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "roadmap": "roadmap.json",
            "gap_analysis": "gap_analysis.json",
            "execution_blueprint": "execution_blueprint.json",
            "broker_blueprint": "broker_blueprint.json",
            "risk_blueprint": "risk_blueprint.json",
            "monitoring_blueprint": "monitoring_blueprint.json",
            "governance_blueprint": "governance_blueprint.json",
            "transition_plan": "transition_plan.json",
            "diagnostics": "diagnostics.json",
            "recommendations": "recommendations.json",
            "summary": "summary.json",
        }
        paths = {}
        for key, filename in mapping.items():
            path = self.output_dir / filename
            self._write(path, payloads.get(key, {}))
            paths[key] = str(path)
        return paths

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
