"""Diagnostics for the research-only knowledge graph."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.knowledge_graph.models import RELATIONSHIP_TYPES  # noqa: E402
from app.knowledge_graph.service import KnowledgeGraphService  # noqa: E402


def main() -> None:
    """Run knowledge graph compliance checks."""
    run = KnowledgeGraphService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/knowledge-graph")
    api_response = client.get("/api/knowledge-graph")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/knowledge_graph.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "knowledge_summary.json",
        "node_report.json",
        "edge_report.json",
        "intelligence_report.json",
        "analytics_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    required_storage = {
        "nodes.json",
        "edges.json",
        "graph_results.json",
        "intelligence_results.json",
        "analytics_results.json",
        "diagnostics.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "knowledge_graph"
    storage_dir = PROJECT_ROOT / "storage" / "knowledge_graph"
    metadata = run.result.metadata
    graph = run.result.graph
    relationship_types = {edge.relationship_type for edge in graph.edges}
    checks = {
        "nodes": graph.node_count >= 10,
        "edges": graph.edge_count >= 8,
        "score": 0 <= graph.knowledge_score <= 100,
        "density": 0 <= graph.relationship_density <= 1,
        "relationships": relationship_types.issubset(set(RELATIONSHIP_TYPES)),
        "intelligence": bool(run.result.intelligence.get("recurring_relationships")),
        "diagnostics": len(run.result.diagnostics) >= 1,
        "recommendations": len(run.result.recommendations) >= 1,
        "storage_paths": all(Path(path).exists() for path in run.storage_paths.values()),
        "report_paths": all(Path(path).exists() for path in run.report_paths.values()),
        "storage_files": required_storage.issubset(
            {path.name for path in storage_dir.glob("*.json")}
        ),
        "report_files": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "خريطة المعرفة البحثية",
                "خريطة المعرفة",
                "توزيع العلاقات",
                "توزيع العقد",
                "أقوى العلاقات",
                "أضعف العلاقات",
                "جودة المعرفة",
            )
        )
        and "Knowledge Graph" not in template_text,
        "research_only": metadata.get("research_only") is True,
        "not_execution": metadata.get("not_execution") is True,
        "not_real_execution": metadata.get("not_real_execution") is True,
        "not_order_placement": metadata.get("not_order_placement") is True,
        "not_broker_access": metadata.get("not_broker_access") is True,
        "not_broker_api": metadata.get("not_broker_api") is True,
        "not_account_login": metadata.get("not_account_login") is True,
        "not_authentication": metadata.get("not_authentication") is True,
        "not_credential_handling": metadata.get("not_credential_handling") is True,
        "not_browser_automation": metadata.get("not_browser_automation") is True,
        "not_real_money": metadata.get("not_real_money") is True,
        "not_live_trading": metadata.get("not_live_trading") is True,
        "not_external_execution_adapter": (
            metadata.get("not_external_execution_adapter") is True
        ),
        "not_trading_automation": metadata.get("not_trading_automation") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
