"""Report writer for trading architecture program outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class TradingArchitectureProgramReportWriter:
    """Write program reports."""

    def __init__(self, output_dir: Path | str = "reports/trading_architecture_program") -> None:
        self.output_dir = Path(output_dir)

    def export(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "summary": "program_summary.json",
            "domains": "domain_report.json",
            "gates": "gate_report.json",
            "workstreams": "workstream_report.json",
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
