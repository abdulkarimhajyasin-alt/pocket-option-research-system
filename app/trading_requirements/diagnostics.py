"""Diagnostics for trading requirements specification outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.trading_requirements.schemas import (
    FORBIDDEN_DECISION_STATES,
    FORBIDDEN_SOURCE_TERMS,
)


class TradingRequirementsDiagnostics:
    """Evaluate requirements outputs and source safety."""

    def evaluate(
        self,
        project_root: Path,
        requirements: dict[str, Any],
        constraints: dict[str, Any],
        go_no_go: dict[str, Any],
    ) -> list[dict[str, str]]:
        diagnostics: list[dict[str, str]] = []
        required_requirements = {"functional", "non_functional", "safety", "risk"}
        required_constraints = {
            "compliance",
            "operational",
            "broker",
            "execution",
            "monitoring",
            "data",
        }
        missing_requirements = required_requirements.difference(requirements)
        missing_constraints = required_constraints.difference(constraints)
        for category in sorted(missing_requirements):
            diagnostics.append(self._item("missing-requirement-category", "مرتفع", category))
        for category in sorted(missing_constraints):
            diagnostics.append(self._item("missing-constraint-category", "مرتفع", category))
        payload_text = str(
            {"requirements": requirements, "constraints": constraints, "go": go_no_go}
        )
        for state in FORBIDDEN_DECISION_STATES:
            if state in payload_text:
                diagnostics.append(self._item("forbidden-decision-state", "مرتفع", state))
        diagnostics.extend(self._source_diagnostics(project_root))
        return diagnostics

    def _source_diagnostics(self, project_root: Path) -> list[dict[str, str]]:
        module_dir = project_root / "app" / "trading_requirements"
        if not module_dir.exists():
            return [self._item("missing-module", "مرتفع", "trading_requirements")]
        text = "\n".join(
            path.read_text(encoding="utf-8").lower() for path in module_dir.glob("*.py")
        )
        return [
            self._item("forbidden-implementation-artifact", "مرتفع", term)
            for term in FORBIDDEN_SOURCE_TERMS
            if term in text
        ]

    def _item(self, code: str, severity: str, message: str) -> dict[str, str]:
        return {"code": code, "severity": severity, "message": message}
