"""Diagnostics for control assurance outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.control_assurance.schemas import FORBIDDEN_READINESS_STATES, FORBIDDEN_SOURCE_TERMS


class ControlAssuranceDiagnostics:
    """Evaluate assurance completeness and source safety."""

    def evaluate(self, project_root: Path, payloads: dict[str, Any]) -> list[dict[str, str]]:
        diagnostics: list[dict[str, str]] = []
        for source in payloads.get("source_inventory", {}).get("missing_sources", []):
            diagnostics.append(
                {"code": "missing-source-output", "severity": "متوسط", "message": str(source)}
            )
        required = {
            "source_inventory",
            "control_quality",
            "evidence_sufficiency",
            "owner_clarity",
            "policy_completeness",
            "gate_maturity",
            "weakness_assessment",
            "audit_readiness",
            "review_readiness",
            "scorecard",
        }
        for key in sorted(required.difference(payloads)):
            diagnostics.append({"code": f"missing-{key}", "severity": "مرتفع", "message": key})
        scorecard = payloads.get("scorecard", {})
        if float(scorecard.get("overall_assurance_score", 0.0)) < 80.0:
            diagnostics.append(
                {"code": "low-assurance-score", "severity": "متوسط", "message": "overall"}
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
        module_dir = project_root / "app" / "control_assurance"
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
