"""Architecture consistency audit engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class ArchitectureAuditEngine:
    """Audit package layout and phase architecture shape."""

    REQUIRED_PACKAGES = (
        "paper_control_center",
        "paper_live_readiness",
        "integration_safety",
        "market_observation",
        "live_observation",
        "signal_stream",
        "paper_execution",
        "paper_portfolio",
    )

    def evaluate(self, project_root: Path) -> dict[str, Any]:
        app_dir = project_root / "app"
        missing = [name for name in self.REQUIRED_PACKAGES if not (app_dir / name).exists()]
        package_count = len([item for item in app_dir.iterdir() if item.is_dir()])
        score = max(0.0, 100.0 - len(missing) * 12.0)
        return {
            "architecture_score": round(score, 2),
            "required_packages": list(self.REQUIRED_PACKAGES),
            "missing_packages": missing,
            "package_count": package_count,
            "architecture_audit_only": True,
        }
