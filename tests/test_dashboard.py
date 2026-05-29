"""Tests for the local research dashboard MVP."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.dashboard.actions import ACTION_DEFINITIONS, DashboardActionRunner
from app.dashboard.report_loader import DashboardReportLoader
from app.dashboard.routes import create_dashboard_app
from app.dashboard.service import DashboardService


def write_dashboard_reports(root: Path) -> None:
    """Create deterministic dashboard report fixtures."""
    reports = root / "reports"
    (reports / "validation").mkdir(parents=True)
    (reports / "datasets").mkdir(parents=True)
    (reports / "validation" / "unit_report.json").write_text(
        json.dumps(
            {
                "report_id": "unit-validation",
                "strategy_name": "research_cisd_fvg_strategy",
                "dataset": {"name": "unit_dataset"},
                "robustness": {"score": 72.5, "category": "Strong"},
                "validation_results": {
                    "walk_forward": {"windows": [{}, {}]},
                    "parameter_sweep": {"results": [{}, {}]},
                    "out_of_sample": {"stability_score": 88.0},
                },
                "overfitting_warnings": [{"severity": "medium", "code": "unit"}],
            }
        ),
        encoding="utf-8",
    )
    (reports / "datasets" / "unit_dataset.json").write_text(
        json.dumps(
            {
                "metadata": {
                    "dataset_id": "dataset-1",
                    "dataset_name": "unit_dataset",
                    "symbol": "EURUSD",
                    "timeframe": "1m",
                    "version": "v1",
                    "row_count": 5,
                    "checksum": "abc",
                },
                "quality": {"quality_score": 99.0, "gaps": []},
                "integrity": {"passed": True, "fingerprint": "fp"},
                "statistics": {"duplicate_count": 0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "summary.txt").write_text("research summary", encoding="utf-8")
    (reports / "table.csv").write_text("name,value\nscore,99\n", encoding="utf-8")


def test_report_loader_parses_json_txt_and_csv(tmp_path: Path) -> None:
    write_dashboard_reports(tmp_path)
    loader = DashboardReportLoader(tmp_path)
    reports = loader.list_reports()
    assert {report.report_type for report in reports} == {"json", "text", "csv"}
    json_report = next(report for report in reports if report.name == "unit_report.json")
    csv_report = next(report for report in reports if report.name == "table.csv")
    txt_report = next(report for report in reports if report.name == "summary.txt")
    assert loader.get_report(json_report.report_id).json_data["report_id"] == "unit-validation"
    assert loader.get_report(csv_report.report_id).csv_rows == [["score", "99"]]
    assert "research summary" in loader.get_report(txt_report.report_id).raw_text


def test_dashboard_service_builds_empty_and_populated_states(tmp_path: Path) -> None:
    empty = DashboardService(tmp_path)
    assert empty.report_loader.list_reports() == []
    assert empty.validation_summaries() == []

    write_dashboard_reports(tmp_path)
    service = DashboardService(tmp_path)
    overview = service.overview()
    assert overview.latest_robustness_score == 72.5
    assert overview.latest_dataset_quality_score == 99.0
    assert overview.warning_counts["medium"] == 1
    assert overview.datasets[0].integrity_status == "passed"


def test_action_allowlist_and_safe_wrapper(tmp_path: Path) -> None:
    runner = DashboardActionRunner(tmp_path)
    assert "validation" in ACTION_DEFINITIONS
    assert all("broker" not in action.name for action in runner.list_actions())
    with pytest.raises(KeyError):
        runner.run("validation;rm")

    completed = Mock(returncode=0, stdout="ok", stderr="")
    with patch("app.dashboard.actions.subprocess.run", return_value=completed) as run_mock:
        result = runner.run("validation")
    assert result.exit_code == 0
    assert result.stdout == "ok"
    command = run_mock.call_args.args[0]
    assert command[1:] == ("scripts/run_validation.py",)
    if "shell" in run_mock.call_args.kwargs:
        assert run_mock.call_args.kwargs["shell"] is False


def test_dashboard_routes_render(tmp_path: Path) -> None:
    write_dashboard_reports(tmp_path)
    templates_src = Path(__file__).resolve().parents[1] / "app" / "templates"
    static_src = Path(__file__).resolve().parents[1] / "app" / "static"
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    import shutil

    shutil.copytree(templates_src, app_dir / "templates")
    shutil.copytree(static_src, app_dir / "static")

    client = TestClient(create_dashboard_app(tmp_path))
    for route in ("/", "/strategies", "/datasets", "/validation", "/reports", "/actions"):
        response = client.get(route)
        assert response.status_code == 200
    assert "local research dashboard" in client.get("/").text.lower()
    assert client.get("/health").json()["status"] == "ok"
