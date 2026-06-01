"""Storage writer for control assurance outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ControlAssuranceStorage:
    """Write assurance artifacts to local storage."""

    def __init__(self, output_dir: Path | str = "storage/control_assurance") -> None:
        self.output_dir = Path(output_dir)

    def save(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "source_inventory": "source_inventory.json",
            "control_quality": "control_quality.json",
            "evidence_sufficiency": "evidence_sufficiency.json",
            "owner_clarity": "owner_clarity.json",
            "policy_completeness": "policy_completeness.json",
            "gate_maturity": "gate_maturity.json",
            "weakness_assessment": "weakness_assessment.json",
            "audit_readiness": "audit_readiness.json",
            "review_readiness": "review_readiness.json",
            "scorecard": "scorecard.json",
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
