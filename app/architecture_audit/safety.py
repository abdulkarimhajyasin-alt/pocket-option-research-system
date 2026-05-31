"""Safety audit engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class SafetyAuditEngine:
    """Verify no unsafe production capability has been introduced."""

    REQUIRED_FLAGS = (
        "not_real_execution",
        "not_broker_access",
        "not_browser_automation",
        "not_authentication",
        "not_credential_handling",
        "not_live_trading",
        "not_external_execution_adapter",
        "not_trading_automation",
    )

    def evaluate(self, project_root: Path, metadata: dict[str, bool]) -> dict[str, Any]:
        missing_flags = [flag for flag in self.REQUIRED_FLAGS if metadata.get(flag) is not True]
        risky_imports = self._risky_imports(project_root / "app")
        score = 100.0 - len(missing_flags) * 8.0 - len(risky_imports) * 20.0
        return {
            "safety_score": round(max(0.0, score), 2),
            "missing_safety_flags": missing_flags,
            "risky_imports": risky_imports,
            "no_execution_paths": metadata.get("not_real_execution") is True,
            "no_broker_paths": metadata.get("not_broker_access") is True,
            "no_login_auth_paths": metadata.get("not_authentication") is True,
            "no_automation_paths": metadata.get("not_browser_automation") is True,
            "no_trading_paths": metadata.get("not_live_trading") is True,
            "architecture_audit_only": True,
        }

    def _risky_imports(self, app_dir: Path) -> list[str]:
        risky_tokens = ("selenium", "playwright")
        hits = []
        for path in app_dir.rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            if any(f"import {token}" in text or f"from {token}" in text for token in risky_tokens):
                hits.append(str(path))
        return hits
