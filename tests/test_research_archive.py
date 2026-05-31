from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.research_archive.diff import ResearchDiffEngine
from app.research_archive.evolution import INSUFFICIENT, ResearchEvolutionEngine
from app.research_archive.schemas import VERSION_PREFIX
from app.research_archive.service import ResearchArchiveService
from app.research_archive.snapshot import ResearchSnapshotEngine
from app.research_archive.versioning import ResearchVersioningEngine


def test_research_archive_snapshot_and_versioning(tmp_path: Path) -> None:
    service = ResearchArchiveService(tmp_path)
    first = service.run_full_archive_cycle()
    second_version, second_record = service.create_archive_version()

    assert first.snapshot.research_only is True
    assert first.version.version_label == f"{VERSION_PREFIX}0001"
    assert second_version.version_label == first.version.version_label
    assert second_record.version_id == first.version.version_id
    assert service.get_latest_version()["version_label"] == f"{VERSION_PREFIX}0001"
    assert len(service.get_version_history()) == 1
    assert first.archive_record.archive_status == "stored"


def test_research_archive_forced_version_and_diff(tmp_path: Path) -> None:
    service = ResearchArchiveService(tmp_path)
    first = service.run_full_archive_cycle()
    second = service.run_full_archive_cycle(force=True)
    diff = service.compare_latest_with_previous()

    assert first.version.version_label == f"{VERSION_PREFIX}0001"
    assert second.version.version_label == f"{VERSION_PREFIX}0002"
    assert diff["from_version"] == f"{VERSION_PREFIX}0001"
    assert diff["to_version"] == f"{VERSION_PREFIX}0002"
    assert diff["research_only"] is True


def test_research_archive_engines_handle_edges(tmp_path: Path) -> None:
    snapshot = ResearchSnapshotEngine(tmp_path).build_snapshot()
    diagnostics = ResearchArchiveService(tmp_path)._diagnostics(snapshot)
    versioning = ResearchVersioningEngine(tmp_path / "storage" / "research_archive")
    diff = ResearchDiffEngine().compare({"a": 1}, {"a": 2, "b": 3}).to_dict()
    evolution = ResearchEvolutionEngine().analyze([], [], diagnostics, []).to_dict()

    assert snapshot.source_summary["missing_source_count"] > 0
    assert diagnostics
    assert versioning.next_version_label([]) == f"{VERSION_PREFIX}0001"
    assert "b" in diff["added_keys"]
    assert diff["improved_metrics"][0]["key"] == "a"
    assert evolution["readiness_trend"] == INSUFFICIENT


def test_research_archive_dashboard_routes_are_safe() -> None:
    ResearchArchiveService(Path(".")).run_full_archive_cycle()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/research-archive",
        "/api/research-archive",
        "/api/research-archive/latest",
        "/api/research-archive/history",
        "/api/research-archive/diff",
        "/api/research-archive/evolution",
        "/api/research-archive/diagnostics",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert "أرشيف البحث" in responses["/research-archive"].text
    assert responses["/api/research-archive"].json()["summary"]["research_only"] is True
    assert responses["/api/research-archive/latest"].json()["safety_boundary"]["research_only"] is True
    assert responses["/api/research-archive/diagnostics"].json()["research_only"] is True
