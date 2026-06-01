"""Storage writer for production system design outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ProductionSystemDesignStorage:
    """Persist design blueprint artifacts."""

    def __init__(self, output_dir: Path | str = "storage/production_system_design") -> None:
        self.output_dir = Path(output_dir)

    def save(self, payloads: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {
            "topology": "topology.json",
            "service_boundaries": "service_boundaries.json",
            "runtime_architecture": "runtime_architecture.json",
            "environment_strategy": "environment_strategy.json",
            "configuration_strategy": "configuration_strategy.json",
            "secrets_strategy": "secrets_strategy.json",
            "database_strategy": "database_strategy.json",
            "event_queue_strategy": "event_queue_strategy.json",
            "logging_strategy": "logging_strategy.json",
            "monitoring_strategy": "monitoring_strategy.json",
            "alerting_strategy": "alerting_strategy.json",
            "incident_response": "incident_response.json",
            "backup_recovery": "backup_recovery.json",
            "release_rollback": "release_rollback.json",
            "readiness_gates": "readiness_gates.json",
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
