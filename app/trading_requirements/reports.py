"""Report writer for trading requirements outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class TradingRequirementsReportWriter:
    """Write requirements reports."""

    def __init__(self, output_dir: Path | str = "reports/trading_requirements") -> None:
        self.output_dir = Path(output_dir)

    def export(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "summary": "requirements_summary.json",
            "functional": "functional_requirements_report.json",
            "non_functional": "non_functional_requirements_report.json",
            "safety": "safety_requirements_report.json",
            "risk": "risk_requirements_report.json",
            "compliance": "compliance_constraints_report.json",
            "operational": "operational_constraints_report.json",
            "broker": "broker_constraints_report.json",
            "execution": "execution_constraints_report.json",
            "monitoring": "monitoring_constraints_report.json",
            "data": "data_constraints_report.json",
            "go_no_go": "go_no_go_report.json",
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
