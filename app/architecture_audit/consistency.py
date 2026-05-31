"""Consistency audit engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class ConsistencyEngine:
    """Audit report, storage, dashboard, route, API, and naming consistency."""

    def evaluate(self, project_root: Path) -> dict[str, Any]:
        reports = sorted((project_root / "reports").glob("*/*.json"))
        storage = sorted((project_root / "storage").glob("*/*.json"))
        templates = sorted((project_root / "app" / "templates" / "dashboard").glob("*.html"))
        route_text = (project_root / "app" / "dashboard" / "routes.py").read_text(
            encoding="utf-8"
        )
        api_count = route_text.count('@app.get("/api/')
        route_count = route_text.count("@app.get(")
        missing_report_pairs = self._missing_counterparts(reports, project_root / "storage")
        score = 100.0
        score -= min(20.0, len(missing_report_pairs) * 0.5)
        score -= 5.0 if api_count < 10 else 0.0
        score -= 5.0 if route_count < api_count else 0.0
        return {
            "consistency_score": round(max(0.0, score), 2),
            "report_count": len(reports),
            "storage_count": len(storage),
            "dashboard_template_count": len(templates),
            "api_route_count": api_count,
            "route_count": route_count,
            "missing_storage_counterparts": missing_report_pairs[:25],
            "architecture_audit_only": True,
        }

    def _missing_counterparts(self, reports: list[Path], storage_root: Path) -> list[str]:
        missing = []
        for report in reports:
            domain = report.parent.name
            if not (storage_root / domain).exists():
                missing.append(domain)
        return sorted(set(missing))
