"""Diagnostics for governance traceability outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.governance_traceability.schemas import (
    FORBIDDEN_READINESS_STATES,
    FORBIDDEN_SOURCE_TERMS,
)


class GovernanceTraceabilityDiagnostics:
    """Evaluate traceability completeness and source safety."""

    def evaluate(self, project_root: Path, payloads: dict[str, Any]) -> list[dict[str, str]]:
        diagnostics: list[dict[str, str]] = []
        sources = payloads.get("source_inventory", {})
        missing_sources = sources.get("missing_sources", [])
        for source in missing_sources:
            diagnostics.append(
                {
                    "code": "missing-source-output",
                    "severity": "متوسط",
                    "message": str(source),
                }
            )
        required = {
            "source_inventory",
            "control_mappings",
            "control_matrix",
            "evidence_matrix",
            "readiness_mapping",
            "risk_mapping",
            "incident_mapping",
            "release_mapping",
            "monitoring_mapping",
            "policy_mapping",
            "coverage_summary",
        }
        for key in sorted(required.difference(payloads)):
            diagnostics.append({"code": f"missing-{key}", "severity": "مرتفع", "message": key})
        coverage = payloads.get("coverage_summary", {})
        if float(coverage.get("overall_traceability_score", 0.0)) < 80.0:
            diagnostics.append(
                {
                    "code": "low-coverage-score",
                    "severity": "متوسط",
                    "message": "overall_traceability_score",
                }
            )
        text = str(payloads)
        for state in FORBIDDEN_READINESS_STATES:
            if state in text:
                diagnostics.append(
                    {
                        "code": "forbidden-readiness-state",
                        "severity": "مرتفع",
                        "message": state,
                    }
                )
        diagnostics.extend(self._source_diagnostics(project_root))
        return diagnostics

    def _source_diagnostics(self, project_root: Path) -> list[dict[str, str]]:
        module_dir = project_root / "app" / "governance_traceability"
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
