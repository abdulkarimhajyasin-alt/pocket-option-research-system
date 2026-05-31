"""Reports for paper portfolio governance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.paper_portfolio.models import PaperPortfolioRun


class PaperPortfolioReportWriter:
    """Write paper portfolio reports."""

    def __init__(self, output_dir: Path | str = "reports/paper_portfolio") -> None:
        self.output_dir = Path(output_dir)

    def export(self, result: PaperPortfolioRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "portfolio_summary.json",
            "exposure": self.output_dir / "exposure_report.json",
            "drawdown": self.output_dir / "drawdown_report.json",
            "governance": self.output_dir / "governance_report.json",
            "limits": self.output_dir / "limits_report.json",
            "analytics": self.output_dir / "analytics_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(paths["summary"], {"summary": result.analytics, "latest": result.to_dict()})
        self._write(paths["exposure"], result.exposure)
        self._write(paths["drawdown"], result.drawdown)
        self._write(paths["governance"], self._count(item.status for item in result.governance))
        self._write(paths["limits"], self._count(item.status for item in result.limits))
        self._write(paths["analytics"], result.analytics)
        self._write(paths["diagnostics"], self._count(item.name for item in result.diagnostics))
        self._write(
            paths["recommendations"],
            self._count(item.title for item in result.recommendations),
        )
        return {key: str(path) for key, path in paths.items()}

    def _count(self, values: Any) -> dict[str, int]:
        counts: dict[str, int] = {}
        for value in values:
            key = str(value)
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
