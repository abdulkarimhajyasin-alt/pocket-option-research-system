"""Report writer for control assurance outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ControlAssuranceReportWriter:
    """Write assurance report artifacts."""

    def __init__(self, output_dir: Path | str = "reports/control_assurance") -> None:
        self.output_dir = Path(output_dir)

    def export(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "summary": "control_assurance_summary.json",
            "source_inventory": "source_inventory_report.json",
            "control_quality": "control_quality_report.json",
            "evidence_sufficiency": "evidence_sufficiency_report.json",
            "owner_clarity": "owner_clarity_report.json",
            "policy_completeness": "policy_completeness_report.json",
            "gate_maturity": "gate_maturity_report.json",
            "weakness_assessment": "weakness_assessment_report.json",
            "audit_readiness": "audit_readiness_report.json",
            "review_readiness": "review_readiness_report.json",
            "scorecard": "scorecard_report.json",
            "diagnostics": "diagnostics_report.json",
            "recommendations": "recommendations_report.json",
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
