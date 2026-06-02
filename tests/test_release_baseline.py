import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.release_baseline.diagnostics import ReleaseBaselineDiagnostics
from app.release_baseline.schemas import FORBIDDEN_BASELINE_STATES, FORBIDDEN_SOURCE_TERMS
from app.release_baseline.service import ReleaseBaselineService


def test_source_loading_handles_missing_optional_files(tmp_path: Path) -> None:
    sources = ReleaseBaselineService(tmp_path).load_sources()

    assert "sources" in sources
    assert "missing_sources" in sources
    assert sources["baseline_reconciliation_only"] is True


def test_full_release_baseline_generation_is_non_destructive(tmp_path: Path) -> None:
    (tmp_path / "reports" / "repository_hygiene").mkdir(parents=True)
    (tmp_path / "storage" / "repository_hygiene").mkdir(parents=True)
    (tmp_path / "phase65.md").write_text("phase", encoding="utf-8")
    run = ReleaseBaselineService(tmp_path).run_full_release_baseline()

    assert run.payloads["baseline_inventory"]["items"]
    assert run.payloads["commit_classification"]["items"]
    assert "items" in run.payloads["artifact_reconciliation"]
    assert "items" in run.payloads["evidence_selection"]
    assert run.payloads["cleanup_checklist"]["items"]
    assert "items" in run.payloads["ignore_review"]
    assert run.payloads["prompt_file_policy"]["items"]
    assert "items" in run.payloads["validation_churn"]
    assert "items" in run.payloads["archive_reconciliation"]
    assert run.payloads["decision_matrix"]["items"]
    assert run.payloads["scorecard"]["overall_baseline_readiness_score"] >= 0
    assert all(
        item["destructive_action_forbidden"] is True
        for item in run.payloads["cleanup_checklist"]["items"]
    )
    assert run.summary["baseline_reconciliation_only"] is True
    assert run.summary["manual_cleanup_planning_only"] is True
    assert run.summary["non_destructive"] is True
    assert run.summary["no_gitignore_modification"] is True
    assert run.summary["no_broker_access"] is True
    assert run.summary["no_execution_capability"] is True
    assert run.summary["no_authentication"] is True
    assert run.summary["no_credentials"] is True
    assert run.summary["no_browser_automation"] is True
    assert run.summary["no_money_handling"] is True


def test_ignore_review_does_not_modify_gitignore(tmp_path: Path) -> None:
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("existing\n", encoding="utf-8")
    before = gitignore.read_text(encoding="utf-8")

    ReleaseBaselineService(tmp_path).build_ignore_review()

    assert gitignore.read_text(encoding="utf-8") == before


def test_forbidden_readiness_states_never_appear(tmp_path: Path) -> None:
    run = ReleaseBaselineService(tmp_path).run_full_release_baseline()
    payload = json.dumps(run.payloads, ensure_ascii=False)

    assert not any(state in payload for state in FORBIDDEN_BASELINE_STATES)


def test_diagnostics_detect_unsafe_destructive_wording(tmp_path: Path) -> None:
    diagnostics = ReleaseBaselineDiagnostics().evaluate(
        tmp_path,
        {"scorecard": {}, "unsafe": "automatic deletion enabled"},
    )
    codes = {item["code"] for item in diagnostics}

    assert "unsafe-wording" in codes
    assert "missing-cleanup_checklist" in codes


def test_recommendations_are_arabic() -> None:
    recommendations = ReleaseBaselineService(Path(".")).generate_recommendations()

    assert len(recommendations) >= 10
    assert any("مراجعة" in item for item in recommendations)


def test_dashboard_and_api_routes() -> None:
    ReleaseBaselineService(Path(".")).run_full_release_baseline()
    client = TestClient(create_dashboard_app(Path(".")))
    routes = (
        "/release-baseline",
        "/api/release-baseline",
        "/api/release-baseline/inventory",
        "/api/release-baseline/commit-classification",
        "/api/release-baseline/artifact-reconciliation",
        "/api/release-baseline/evidence",
        "/api/release-baseline/cleanup-checklist",
        "/api/release-baseline/ignore-review",
        "/api/release-baseline/prompt-policy",
        "/api/release-baseline/validation-churn",
        "/api/release-baseline/archive-reconciliation",
        "/api/release-baseline/decision-matrix",
        "/api/release-baseline/scorecard",
        "/api/release-baseline/diagnostics",
        "/api/release-baseline/recommendations",
    )
    responses = {route: client.get(route) for route in routes}

    assert all(response.status_code == 200 for response in responses.values())
    assert "خط أساس الإصدار" in responses["/release-baseline"].text
    assert responses["/api/release-baseline"].json()["summary"]["non_destructive"] is True


def test_generated_json_files_are_valid(tmp_path: Path) -> None:
    run = ReleaseBaselineService(tmp_path).run_full_release_baseline()

    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())
    for path in list(run.storage_paths.values()) + list(run.report_paths.values()):
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_module_has_no_forbidden_capability() -> None:
    module_dir = Path("app/release_baseline")
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()

    assert not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS)
