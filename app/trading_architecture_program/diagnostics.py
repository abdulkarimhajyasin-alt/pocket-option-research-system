"""Diagnostics for the trading architecture program foundation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.trading_architecture_program.schemas import FORBIDDEN_SOURCE_TERMS


class TradingArchitectureProgramDiagnostics:
    """Evaluate program artifacts and source safety."""

    def evaluate(
        self,
        project_root: Path,
        registry: dict[str, Any] | None = None,
        domains: list[dict[str, Any]] | None = None,
        gates: list[dict[str, Any]] | None = None,
        workstreams: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, str]]:
        diagnostics: list[dict[str, str]] = []
        if not registry:
            diagnostics.append(self._item("missing-registry", "مرتفع", "Missing program registry."))
        if len(domains or []) != 8:
            diagnostics.append(self._item("domain-count", "متوسط", "Expected 8 domains."))
        if len(gates or []) != 7:
            diagnostics.append(self._item("gate-count", "متوسط", "Expected 7 gates."))
        if len(workstreams or []) != 8:
            diagnostics.append(self._item("workstream-count", "متوسط", "Expected 8 workstreams."))
        for gate in gates or []:
            if gate.get("may_approve_live_trading"):
                diagnostics.append(
                    self._item(
                        "unsafe-gate",
                        "مرتفع",
                        "A decision gate may approve live trading.",
                    )
                )
        diagnostics.extend(self._source_diagnostics(project_root))
        return diagnostics

    def _source_diagnostics(self, project_root: Path) -> list[dict[str, str]]:
        module_dir = project_root / "app" / "trading_architecture_program"
        if not module_dir.exists():
            return [self._item("missing-module", "مرتفع", "Module is missing.")]
        text = "\n".join(
            path.read_text(encoding="utf-8").lower() for path in module_dir.glob("*.py")
        )
        return [
            self._item(
                "forbidden-implementation-artifact",
                "مرتفع",
                f"Forbidden implementation artifact detected: {term}",
            )
            for term in FORBIDDEN_SOURCE_TERMS
            if term in text
        ]

    def _item(self, code: str, severity: str, message: str) -> dict[str, str]:
        return {"code": code, "severity": severity, "message": message}
