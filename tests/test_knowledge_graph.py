from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.knowledge_graph.models import RELATIONSHIP_TYPES
from app.knowledge_graph.service import KnowledgeGraphService


def test_knowledge_graph_service_generates_outputs() -> None:
    run = KnowledgeGraphService(Path(".")).run()

    assert run.result.graph.node_count >= 10
    assert run.result.graph.edge_count >= 8
    assert 0 <= run.result.graph.knowledge_score <= 100
    assert 0 <= run.result.graph.relationship_density <= 1
    assert run.result.metadata["research_only"] is True
    assert run.result.metadata["not_execution"] is True
    assert run.result.metadata["not_broker_access"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_knowledge_graph_relationships_and_intelligence() -> None:
    run = KnowledgeGraphService(Path(".")).run()
    relationship_types = {edge.relationship_type for edge in run.result.graph.edges}

    assert relationship_types.issubset(set(RELATIONSHIP_TYPES))
    assert run.result.graph.strongest_relationship != "غير متاح"
    assert run.result.graph.weakest_relationship != "غير متاح"
    assert run.result.intelligence["recurring_relationships"]
    assert "asset_pattern_relationships" in run.result.intelligence
    assert "session_pattern_relationships" in run.result.intelligence
    assert "regime_pattern_relationships" in run.result.intelligence


def test_knowledge_graph_dashboard_and_api_are_arabic() -> None:
    KnowledgeGraphService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/knowledge-graph")
    api = client.get("/api/knowledge-graph")

    assert page.status_code == 200
    assert api.status_code == 200
    assert "خريطة المعرفة البحثية" in page.text
    assert "خريطة المعرفة" in page.text
    assert "توزيع العلاقات" in page.text
    assert "أقوى العلاقات" in page.text
    assert "Knowledge Graph" not in page.text
    assert api.json()["summary"]["research_only"] is True
