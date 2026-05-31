"""Storage for the research knowledge graph."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.knowledge_graph.models import KnowledgeGraphRun


class KnowledgeGraphStorage:
    """Persist graph nodes, edges, metrics, intelligence, and diagnostics."""

    def __init__(self, output_dir: Path | str = "storage/knowledge_graph") -> None:
        self.output_dir = Path(output_dir)

    def save(self, result: KnowledgeGraphRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "nodes": self.output_dir / "nodes.json",
            "edges": self.output_dir / "edges.json",
            "graph": self.output_dir / "graph_results.json",
            "intelligence": self.output_dir / "intelligence_results.json",
            "analytics": self.output_dir / "analytics_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["nodes"], [item.to_dict() for item in result.graph.nodes])
        self._write(paths["edges"], [item.to_dict() for item in result.graph.edges])
        self._write(paths["graph"], result.graph.to_dict())
        self._write(paths["intelligence"], result.intelligence)
        self._write(paths["analytics"], result.analytics)
        self._write(paths["diagnostics"], result.to_dict())
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
