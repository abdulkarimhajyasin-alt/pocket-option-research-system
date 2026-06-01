"""Storage writer for trading requirements outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class TradingRequirementsStorage:
    """Persist requirements specification artifacts."""

    def __init__(self, output_dir: Path | str = "storage/trading_requirements") -> None:
        self.output_dir = Path(output_dir)

    def save(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "functional": "functional_requirements.json",
            "non_functional": "non_functional_requirements.json",
            "safety": "safety_requirements.json",
            "risk": "risk_requirements.json",
            "compliance": "compliance_constraints.json",
            "operational": "operational_constraints.json",
            "broker": "broker_constraints.json",
            "execution": "execution_constraints.json",
            "monitoring": "monitoring_constraints.json",
            "data": "data_constraints.json",
            "go_no_go": "go_no_go_criteria.json",
            "coverage": "coverage_summary.json",
            "diagnostics": "diagnostics.json",
            "recommendations": "recommendations.json",
            "summary": "summary.json",
        }
        paths = {}
        for key, filename in mapping.items():
            path = self.output_dir / filename
            path.write_text(
                json.dumps(payloads.get(key, {}), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            paths[key] = str(path)
        return paths
