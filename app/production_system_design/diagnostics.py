"""Diagnostics for production system design outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.production_system_design.schemas import (
    FORBIDDEN_READINESS_STATES,
    FORBIDDEN_SOURCE_TERMS,
)


class ProductionSystemDesignDiagnostics:
    """Evaluate design completeness and source safety."""

    def evaluate(self, project_root: Path, payloads: dict[str, Any]) -> list[dict[str, str]]:
        diagnostics: list[dict[str, str]] = []
        required = {
            "topology",
            "service_boundaries",
            "runtime_architecture",
            "environment_strategy",
            "configuration_strategy",
            "secrets_strategy",
            "database_strategy",
            "event_queue_strategy",
            "logging_strategy",
            "monitoring_strategy",
            "alerting_strategy",
            "incident_response",
            "backup_recovery",
            "release_rollback",
            "readiness_gates",
        }
        for key in sorted(required.difference(payloads)):
            diagnostics.append({"code": f"missing-{key}", "severity": "مرتفع", "message": key})
        text = str(payloads)
        for state in FORBIDDEN_READINESS_STATES:
            if state in text:
                diagnostics.append(
                    {"code": "forbidden-readiness-state", "severity": "مرتفع", "message": state}
                )
        diagnostics.extend(self._source_diagnostics(project_root))
        return diagnostics

    def _source_diagnostics(self, project_root: Path) -> list[dict[str, str]]:
        module_dir = project_root / "app" / "production_system_design"
        if not module_dir.exists():
            return [{"code": "missing-module", "severity": "مرتفع", "message": "module"}]
        text = "\n".join(
            path.read_text(encoding="utf-8").lower() for path in module_dir.glob("*.py")
        )
        return [
            {
                "code": "forbidden-implementation-artifact",
                "severity": "مرتفع",
                "message": term,
            }
            for term in FORBIDDEN_SOURCE_TERMS
            if term in text
        ]
