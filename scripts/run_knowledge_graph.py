"""Run the research-only knowledge graph."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.knowledge_graph.service import KnowledgeGraphService  # noqa: E402


def main() -> None:
    """Generate knowledge graph storage and reports."""
    run = KnowledgeGraphService(PROJECT_ROOT).run()
    graph = run.result.graph
    print("Knowledge graph generated")
    print(f"node_count={graph.node_count}")
    print(f"edge_count={graph.edge_count}")
    print(f"knowledge_score={graph.knowledge_score}")
    print("research_only=True")
    print("not_execution=True")
    print("not_broker_access=True")
    print("not_live_trading=True")
    print(f"storage={run.storage_paths}")
    print(f"reports={run.report_paths}")


if __name__ == "__main__":
    main()
