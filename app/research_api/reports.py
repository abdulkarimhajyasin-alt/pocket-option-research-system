"""Reports for unified research API outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.research_api.models import UnifiedResearchSnapshot


class ResearchAPIReportWriter:
    """Write unified research API reports."""

    def __init__(self, output_dir: Path | str = "reports/research_api") -> None:
        self.output_dir = Path(output_dir)

    def export(self, snapshot: UnifiedResearchSnapshot) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "research_summary.json",
            "signals": self.output_dir / "signal_intelligence_view.json",
            "opportunities": self.output_dir / "opportunity_view.json",
            "paper": self.output_dir / "paper_trading_view.json",
            "readiness": self.output_dir / "readiness_view.json",
            "knowledge_graph": self.output_dir / "knowledge_graph_summary.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(paths["summary"], snapshot.to_dict())
        self._write(paths["signals"], snapshot.signals.to_dict())
        self._write(paths["opportunities"], snapshot.opportunities.to_dict())
        self._write(paths["paper"], snapshot.paper.to_dict())
        self._write(paths["readiness"], snapshot.readiness.to_dict())
        self._write(paths["knowledge_graph"], snapshot.knowledge_graph.to_dict())
        self._write(paths["diagnostics"], snapshot.diagnostics.to_dict())
        self._write(paths["recommendations"], snapshot.recommendations.to_dict())
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
