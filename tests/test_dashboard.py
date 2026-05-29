"""Tests for the local research dashboard MVP."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.dashboard.actions import ACTION_DEFINITIONS, DashboardActionRunner
from app.dashboard.analytics import DashboardAnalyticsService
from app.dashboard.charts import bar_chart, line_chart
from app.dashboard.metrics import DashboardMetricsService
from app.dashboard.report_loader import DashboardReportLoader
from app.dashboard.routes import create_dashboard_app
from app.dashboard.service import DashboardService
from app.i18n import get_translations, translate


def write_dashboard_reports(root: Path) -> None:
    """Create deterministic dashboard report fixtures."""
    reports = root / "reports"
    (reports / "validation").mkdir(parents=True)
    (reports / "datasets").mkdir(parents=True)
    (reports / "analytics").mkdir(parents=True)
    (reports / "strategy_research").mkdir(parents=True)
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
                "quality": {
                    "quality_score": 99.0,
                    "gaps": [],
                    "components": {"missing_data": 99.0, "duplicates": 100.0},
                },
                "integrity": {"passed": True, "fingerprint": "fp"},
                "statistics": {"duplicate_count": 0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "analytics" / "unit_equity.json").write_text(
        json.dumps(
            [
                {
                    "timestamp": "2026-01-01T00:00:00+00:00",
                    "equity": 1,
                    "cumulative_pnl": 1,
                    "drawdown": 0,
                },
                {
                    "timestamp": "2026-01-01T00:01:00+00:00",
                    "equity": -1,
                    "cumulative_pnl": -1,
                    "drawdown": 2,
                },
                {
                    "timestamp": "2026-01-01T00:02:00+00:00",
                    "equity": 2,
                    "cumulative_pnl": 2,
                    "drawdown": 0,
                },
            ]
        ),
        encoding="utf-8",
    )
    (reports / "strategy_research" / "unit_summary.json").write_text(
        json.dumps(
            {
                "strategy_name": "research_cisd_fvg_strategy",
                "generated_signals": 3,
                "bullish_signals": 2,
                "bearish_signals": 1,
                "decision_distribution": {"rejected": 4, "signal": 3},
                "average_confidence_by_evidence": {"trend": 0.7, "session": 0.5},
                "session_quality": {"asian": {"signals": 3, "average_confidence": 0.7}},
            }
        ),
        encoding="utf-8",
    )
    (reports / "summary.txt").write_text("research summary", encoding="utf-8")
    (reports / "table.csv").write_text("name,value\nscore,99\n", encoding="utf-8")


def test_arabic_translation_foundation() -> None:
    translations = get_translations("ar")
    assert translations["nav"]["signals"] == "الإشارات"
    assert translate("pages.overview") == "محطة البحث"
    assert get_translations("fr")["app"]["title"] == translations["app"]["title"]


def test_chart_builders_create_framework_neutral_payloads() -> None:
    line = line_chart("Equity", ["a", "b"], [1.0, 2.0], label="equity").to_dict()
    bars = bar_chart("Signals", ["long", "short"], [2, 1], label="signals").to_dict()
    assert line["summary"]["latest"] == 2.0
    assert bars["chart_type"] == "bar"


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


def test_visualization_services_build_metrics_charts_and_insights(tmp_path: Path) -> None:
    write_dashboard_reports(tmp_path)
    analytics = DashboardAnalyticsService(tmp_path)
    metrics = DashboardMetricsService(tmp_path)

    workbench = metrics.workbench()
    signal_analytics = analytics.signal_analytics()
    dataset_analytics = analytics.dataset_analytics()
    validation_analytics = analytics.validation_analytics()
    equity_analytics = analytics.equity_analytics()

    assert workbench["health"]["status"] in {"healthy", "warning", "critical"}
    assert len(workbench["metrics"]) == 8
    assert workbench["workflow"][-1]["status"] == "complete"
    assert signal_analytics["total_signals"] == 3
    assert dataset_analytics["quality"]["labels"] == ["missing_data", "duplicates"]
    assert validation_analytics["history"]["chart_type"] == "line"
    assert equity_analytics["summary"]["max_drawdown"] == 2.0


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
    for route in (
        "/",
        "/strategies",
        "/datasets",
        "/validation",
        "/signals",
        "/reports",
        "/actions",
    ):
        response = client.get(route)
        assert response.status_code == 200
    assert "منصة البحث الكمي" in client.get("/").text
    assert client.get("/api/signals").json()["total_signals"] == 3
    assert client.get("/api/dashboard").json()["health"]["status"] in {
        "healthy",
        "warning",
        "critical",
    }
    assert client.get("/health").json()["status"] == "ok"
