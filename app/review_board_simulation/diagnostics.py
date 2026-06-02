"""Diagnostics for review board simulation outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.review_board_simulation.schemas import (
    FORBIDDEN_DECISION_STATES,
    FORBIDDEN_SOURCE_TERMS,
)


class ReviewBoardSimulationDiagnostics:
    """Evaluate simulation completeness and source safety."""

    REQUIRED_PAYLOADS = {
        "source_inventory",
        "board_registry",
        "board_simulation_results",
        "gate_dry_run_results",
        "evidence_review",
        "blocker_analysis",
        "decision_scores",
        "findings",
        "readiness_summary",
    }

    def evaluate(self, project_root: Path, payloads: dict[str, Any]) -> list[dict[str, str]]:
        diagnostics: list[dict[str, str]] = []
        for source in payloads.get("source_inventory", {}).get("missing_sources", []):
            diagnostics.append(
                {"code": "missing-source-output", "severity": "متوسط", "message": str(source)}
            )
        for key in sorted(self.REQUIRED_PAYLOADS.difference(payloads)):
            diagnostics.append({"code": f"missing-{key}", "severity": "مرتفع", "message": key})
        scores = payloads.get("decision_scores", {})
        if float(scores.get("overall_review_readiness_score", 0.0)) < 80.0:
            diagnostics.append(
                {"code": "low-review-readiness-score", "severity": "متوسط", "message": "overall"}
            )
        if float(scores.get("gate_readiness_score", 0.0)) < 80.0:
            diagnostics.append(
                {"code": "low-gate-readiness-score", "severity": "متوسط", "message": "gates"}
            )
        if payloads.get("blocker_analysis", {}).get("items"):
            diagnostics.append(
                {"code": "unresolved-blockers", "severity": "مرتفع", "message": "blockers"}
            )
        text = str(payloads)
        for state in FORBIDDEN_DECISION_STATES:
            if state in text:
                diagnostics.append(
                    {"code": "forbidden-decision-state", "severity": "مرتفع", "message": state}
                )
        unsafe_terms = (
            "live trading approval",
            "broker-ready",
            "execution-ready",
            "operational approval for trading",
        )
        for term in unsafe_terms:
            if term in text.lower():
                diagnostics.append(
                    {"code": "unsafe-wording", "severity": "مرتفع", "message": term}
                )
        diagnostics.extend(self._source_diagnostics(project_root))
        template = (
            project_root
            / "app"
            / "templates"
            / "dashboard"
            / "review_board_simulation.html"
        )
        if not template.exists():
            diagnostics.append(
                {
                    "code": "missing-dashboard-integration",
                    "severity": "متوسط",
                    "message": "template",
                }
            )
        ar_file = project_root / "app" / "i18n" / "ar.py"
        if (
            ar_file.exists()
            and "review_board_simulation" not in ar_file.read_text(encoding="utf-8")
        ):
            diagnostics.append(
                {"code": "missing-arabic-labels", "severity": "متوسط", "message": "i18n"}
            )
        return diagnostics

    def _source_diagnostics(self, project_root: Path) -> list[dict[str, str]]:
        module_dir = project_root / "app" / "review_board_simulation"
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
