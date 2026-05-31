"""Diagnostics for final research platform certification."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class PlatformCertificationDiagnostics:
    """Generate deterministic diagnostics from local report availability."""

    def domain_diagnostics(
        self,
        domain_id: str,
        missing: list[str],
        unsafe: bool = False,
    ) -> list[dict[str, Any]]:
        diagnostics: list[dict[str, Any]] = []
        if missing:
            diagnostics.append(
                {
                    "code": f"{domain_id}_missing_reports",
                    "severity": "متوسط",
                    "message": "توجد مخرجات محلية مفقودة لهذا المجال.",
                    "missing": missing,
                }
            )
        if unsafe:
            diagnostics.append(
                {
                    "code": f"{domain_id}_safety_inconsistency",
                    "severity": "مرتفع",
                    "message": "تم رصد عدم اتساق في حدود السلامة البحثية.",
                }
            )
        return diagnostics

    def aggregate(self, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
        diagnostics: list[dict[str, Any]] = []
        for domain in domains:
            diagnostics.extend(domain.get("diagnostics", []))
        return diagnostics

    def unsafe_metadata(self, payload: dict[str, Any]) -> bool:
        text = str(payload)
        forbidden = (
            "Approved For Live Trading",
            "Approved For Execution",
            "Broker Ready",
        )
        return any(item in text for item in forbidden)

    def existing_count(
        self,
        root: Path,
        paths: tuple[tuple[str, ...], ...],
    ) -> tuple[int, list[str]]:
        missing = []
        for parts in paths:
            if not root.joinpath(*parts).exists():
                missing.append("/".join(parts))
        return len(paths) - len(missing), missing
