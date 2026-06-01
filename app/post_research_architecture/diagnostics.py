"""Diagnostics for post-research strategic architecture outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.post_research_architecture.schemas import (
    FORBIDDEN_SOURCE_TERMS,
    UNSAFE_STATE_PHRASES,
)


class PostResearchArchitectureDiagnostics:
    """Evaluate planning outputs and source safety indicators."""

    def evaluate(
        self,
        project_root: Path,
        roadmap: dict[str, Any] | None = None,
        gaps: dict[str, Any] | None = None,
        blueprints: dict[str, dict[str, Any]] | None = None,
        transition: dict[str, Any] | None = None,
        summary: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        diagnostics: list[dict[str, Any]] = []
        if not roadmap:
            diagnostics.append(self._item("missing-roadmap", "مرتفع", "Missing roadmap output."))
        if not gaps:
            diagnostics.append(self._item("missing-gaps", "مرتفع", "Missing gap analysis."))
        blueprints = blueprints or {}
        for key in ("execution", "broker", "risk", "monitoring", "governance"):
            if not blueprints.get(key):
                diagnostics.append(
                    self._item(f"missing-{key}-blueprint", "مرتفع", f"Missing {key} blueprint.")
                )
        if not transition:
            diagnostics.append(
                self._item("missing-transition-plan", "متوسط", "Missing transition plan.")
            )
        if summary and not summary.get("architecture_only"):
            diagnostics.append(
                self._item("unclear-boundary", "مرتفع", "Summary is not architecture-only.")
            )
        diagnostics.extend(self._source_diagnostics(project_root))
        payload = {
            "roadmap": roadmap or {},
            "gaps": gaps or {},
            "blueprints": blueprints,
            "transition": transition or {},
            "summary": summary or {},
        }
        text = str(payload)
        for phrase in UNSAFE_STATE_PHRASES:
            if phrase in text:
                diagnostics.append(
                    self._item("unsafe-state-wording", "مرتفع", f"Unsafe wording: {phrase}")
                )
        return diagnostics

    def _source_diagnostics(self, project_root: Path) -> list[dict[str, Any]]:
        module_dir = project_root / "app" / "post_research_architecture"
        if not module_dir.exists():
            return [
                self._item(
                    "missing-module",
                    "مرتفع",
                    "Post-research architecture module is missing.",
                )
            ]
        text = "\n".join(
            path.read_text(encoding="utf-8").lower() for path in module_dir.glob("*.py")
        )
        diagnostics = []
        for term in FORBIDDEN_SOURCE_TERMS:
            if term in text:
                diagnostics.append(
                    self._item(
                        "forbidden-implementation-artifact",
                        "مرتفع",
                        f"Forbidden implementation artifact detected: {term}",
                    )
                )
        return diagnostics

    def _item(self, code: str, severity: str, message: str) -> dict[str, str]:
        return {"code": code, "severity": severity, "message": message}
