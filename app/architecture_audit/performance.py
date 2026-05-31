"""Performance audit engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class PerformanceAuditEngine:
    """Audit report load, storage growth, dashboard complexity, and orchestration."""

    def evaluate(self, project_root: Path) -> dict[str, Any]:
        reports = sorted((project_root / "reports").glob("*/*.json"))
        storage = sorted((project_root / "storage").glob("*/*.json"))
        report_bytes = sum(path.stat().st_size for path in reports)
        storage_bytes = sum(path.stat().st_size for path in storage)
        analytics_text = (project_root / "app" / "dashboard" / "analytics.py").read_text(
            encoding="utf-8"
        )
        analytics_methods = analytics_text.count("_analytics(")
        service_count = len(list((project_root / "app").glob("*/service.py")))
        score = 100.0
        score -= min(20.0, len(reports) / 50.0)
        score -= min(20.0, (report_bytes + storage_bytes) / 2_000_000.0)
        score -= min(10.0, analytics_methods / 20.0)
        score -= min(10.0, service_count / 20.0)
        return {
            "performance_score": round(max(0.0, score), 2),
            "report_count": len(reports),
            "storage_count": len(storage),
            "report_bytes": report_bytes,
            "storage_bytes": storage_bytes,
            "dashboard_analytics_methods": analytics_methods,
            "service_orchestration_count": service_count,
            "architecture_audit_only": True,
        }
