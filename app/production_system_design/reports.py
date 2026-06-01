"""Report writer for production system design outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ProductionSystemDesignReportWriter:
    """Write design blueprint report artifacts."""

    def __init__(self, output_dir: Path | str = "reports/production_system_design") -> None:
        self.output_dir = Path(output_dir)

    def export(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "summary": "production_design_summary.json",
            "topology": "topology_report.json",
            "service_boundaries": "service_boundaries_report.json",
            "runtime_architecture": "runtime_architecture_report.json",
            "environment_strategy": "environment_strategy_report.json",
            "configuration_strategy": "configuration_strategy_report.json",
            "secrets_strategy": "secrets_strategy_report.json",
            "database_strategy": "database_strategy_report.json",
            "event_queue_strategy": "event_queue_strategy_report.json",
            "logging_strategy": "logging_strategy_report.json",
            "monitoring_strategy": "monitoring_strategy_report.json",
            "alerting_strategy": "alerting_strategy_report.json",
            "incident_response": "incident_response_report.json",
            "backup_recovery": "backup_recovery_report.json",
            "release_rollback": "release_rollback_report.json",
            "readiness_gates": "readiness_gates_report.json",
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
