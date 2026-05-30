"""Deterministic reports for research operations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ResearchOperationsReportWriter:
    """Write executive research operations reports."""

    def __init__(self, output_dir: Path | str = "reports/research_ops") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "executive": self.output_dir / "executive_report.json",
            "health": self.output_dir / "health_report.json",
            "alerts": self.output_dir / "alerts_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
            "risk": self.output_dir / "risk_report.json",
            "summary": self.output_dir / "operations_summary.json",
        }
        self._write(paths["executive"], analytics.get("latest", {}))
        self._write(paths["health"], analytics.get("health_trends", {}))
        self._write(paths["alerts"], analytics.get("alert_distribution", {}))
        self._write(
            paths["recommendations"],
            analytics.get("recommendation_distribution", {}),
        )
        self._write(paths["risk"], analytics.get("risk_distribution", {}))
        self._write(
            paths["summary"],
            {
                "summary": analytics.get("summary", {}),
                "health_trends": analytics.get("health_trends", {}),
                "readiness_trends": analytics.get("readiness_trends", {}),
                "confluence_trends": analytics.get("confluence_trends", {}),
                "performance_trends": analytics.get("performance_trends", {}),
                "opportunity_quality_trends": analytics.get(
                    "opportunity_quality_trends",
                    {},
                ),
                "quality_trends": analytics.get("quality_trends", {}),
                "stability_trends": analytics.get("stability_trends", {}),
                "latest": analytics.get("latest", {}),
            },
        )
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
