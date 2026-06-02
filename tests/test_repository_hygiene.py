import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.repository_hygiene.diagnostics import RepositoryHygieneDiagnostics
from app.repository_hygiene.git_status_parser import GitStatusParser
from app.repository_hygiene.schemas import FORBIDDEN_SOURCE_TERMS
from app.repository_hygiene.service import RepositoryHygieneService


def test_git_status_parser_handles_sample_porcelain() -> None:
    result = GitStatusParser(Path(".")).parse(
        " M reports/example.json\n?? storage/research_archive/diffs/demo.json\n"
    )

    assert result["summary"]["modified"] == 1
    assert result["summary"]["untracked"] == 1
    assert result["items"][1]["category"] == "diff artifact"


def test_git_status_parser_handles_unavailable_git() -> None:
    result = GitStatusParser(Path(".")).parse_unavailable()

    assert result["git_unavailable"] is True
    assert result["repository_hygiene_only"] is True


def test_repository_hygiene_generation_is_non_destructive(tmp_path: Path) -> None:
    (tmp_path / "reports").mkdir()
    (tmp_path / "storage" / "research_archive" / "snapshots" / "research-v0001").mkdir(
        parents=True
    )
    (tmp_path / "reports" / "summary.json").write_text("{}", encoding="utf-8")
    (
        tmp_path
        / "storage"
        / "research_archive"
        / "snapshots"
        / "research-v0001"
        / "snapshot.json"
    ).write_text("{}", encoding="utf-8")
    run = RepositoryHygieneService(tmp_path).run_full_repository_hygiene()

    assert run.payloads["artifact_inventory"]["items"]
    assert run.payloads["artifact_classification"]["items"]
    assert run.payloads["retention_policy"]["items"]
    assert run.payloads["cleanup_plan"]["items"]
    assert run.payloads["ignore_recommendations"]["items"]
    assert "items" in run.payloads["duplicate_artifacts"]
    assert "items" in run.payloads["stale_artifacts"]
    assert run.payloads["archive_policy"]["rule"]
    assert run.payloads["scorecard"]["overall_repository_hygiene_score"] >= 0
    assert all(
        item["destructive_action_forbidden"] is True
        for item in run.payloads["cleanup_plan"]["items"]
    )
    assert run.summary["repository_hygiene_only"] is True
    assert run.summary["artifact_policy_only"] is True
    assert run.summary["non_destructive"] is True
    assert run.summary["no_broker_access"] is True
    assert run.summary["no_execution_capability"] is True
    assert run.summary["no_authentication"] is True
    assert run.summary["no_credentials"] is True
    assert run.summary["no_browser_automation"] is True
    assert run.summary["no_money_handling"] is True


def test_duplicate_and_stale_detection_work(tmp_path: Path) -> None:
    storage = tmp_path / "storage" / "research_archive" / "snapshots"
    (storage / "research-v0001").mkdir(parents=True)
    (storage / "research-v0009").mkdir(parents=True)
    (storage / "research-v0001" / "summary.json").write_text("{}", encoding="utf-8")
    (storage / "research-v0009" / "summary.json").write_text("{}", encoding="utf-8")
    service = RepositoryHygieneService(tmp_path)

    duplicates = service.detect_duplicates()
    stale = service.detect_stale_artifacts()

    assert duplicates["items"]
    assert stale["items"]


def test_diagnostics_detect_unsafe_wording(tmp_path: Path) -> None:
    diagnostics = RepositoryHygieneDiagnostics().evaluate(
        tmp_path,
        {"scorecard": {}, "unsafe": "automatic deletion enabled"},
    )
    codes = {item["code"] for item in diagnostics}

    assert "unsafe-wording" in codes
    assert "missing-cleanup_plan" in codes


def test_recommendations_are_arabic() -> None:
    recommendations = RepositoryHygieneService(Path(".")).generate_recommendations()

    assert len(recommendations) >= 10
    assert any("مراجعة" in item for item in recommendations)


def test_dashboard_and_api_routes() -> None:
    RepositoryHygieneService(Path(".")).run_full_repository_hygiene()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/repository-hygiene",
        "/api/repository-hygiene",
        "/api/repository-hygiene/git-status",
        "/api/repository-hygiene/artifacts",
        "/api/repository-hygiene/retention-policy",
        "/api/repository-hygiene/cleanup-plan",
        "/api/repository-hygiene/ignore-recommendations",
        "/api/repository-hygiene/duplicates",
        "/api/repository-hygiene/stale",
        "/api/repository-hygiene/archive-policy",
        "/api/repository-hygiene/scorecard",
        "/api/repository-hygiene/diagnostics",
        "/api/repository-hygiene/recommendations",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert "نظافة المستودع" in responses["/repository-hygiene"].text
    assert responses["/api/repository-hygiene"].json()["summary"]["non_destructive"] is True


def test_generated_json_files_are_valid(tmp_path: Path) -> None:
    run = RepositoryHygieneService(tmp_path).run_full_repository_hygiene()

    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())
    for path in list(run.storage_paths.values()) + list(run.report_paths.values()):
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_module_has_no_forbidden_capability() -> None:
    module_dir = Path("app/repository_hygiene")
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()

    assert not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS)
