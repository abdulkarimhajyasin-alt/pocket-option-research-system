"""Report writer for the research knowledge graph."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.knowledge_graph.models import KnowledgeGraphRun


class KnowledgeGraphReportWriter:
    """Write graph reports."""

    def __init__(self, output_dir: Path | str = "reports/knowledge_graph") -> None:
        self.output_dir = Path(output_dir)

    def export(self, result: KnowledgeGraphRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "knowledge_summary.json",
            "nodes": self.output_dir / "node_report.json",
            "edges": self.output_dir / "edge_report.json",
            "intelligence": self.output_dir / "intelligence_report.json",
            "analytics": self.output_dir / "analytics_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(
            paths["summary"],
            {"summary": result.graph.to_dict(), "latest": result.to_dict()},
        )
        self._write(paths["nodes"], self._count(node.entity_type for node in result.graph.nodes))
        self._write(
            paths["edges"],
            self._count(edge.relationship_type for edge in result.graph.edges),
        )
        self._write(paths["intelligence"], result.intelligence)
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
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
