"""Phase 19 dashboard UX and research decision tests."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.decision import (
    dataset_decision,
    executive_summary,
    health_score,
    research_decision,
    validation_decision,
)
from app.dashboard.formatting import (
    UNAVAILABLE,
    format_datetime,
    format_number,
    format_percent,
    format_relative_time,
)
from app.dashboard.routes import create_dashboard_app
from app.dashboard.service import DashboardService
from test_dashboard import write_dashboard_reports


def test_arabic_date_time_and_numeric_formatting() -> None:
    assert format_datetime("2026-05-29T19:42:00+00:00") != "2026-05-29T19:42:00+00:00"
    assert format_datetime(None) == UNAVAILABLE
    assert format_relative_time(
        "2026-05-29T19:37:00+00:00",
        now=datetime(2026, 5, 29, 19, 42, tzinfo=UTC),
    ) == "منذ 5 دقيقة"
    assert format_percent(100.0) == "100%"
    assert format_percent(54.0) == "54%"
    assert format_number(2.599999999999998) == "2.60"
    assert format_number(0) == "0"
    assert format_number("n/a") == UNAVAILABLE


def test_research_decision_engine_and_health_score(tmp_path: Path) -> None:
    write_dashboard_reports(tmp_path)
    overview = DashboardService(tmp_path).overview()
    dataset = overview.datasets[0]
    validation = overview.validations[0]

    assert dataset_decision(dataset).status == "صالح للاختبار"
    assert validation_decision(validation).status == "يحتاج تحسين"
    assert research_decision(overview).status == "يحتاج تحسين"

    score = health_score(
        overview,
        now=datetime(2026, 1, 1, 0, 10, tzinfo=UTC),
    )
    assert 0 <= score.score <= 100
    assert score.label in {"ممتاز", "جيد", "متوسط", "ضعيف", "غير كاف"}
    assert "ربحية" in score.explanation


def test_overview_executive_panel_data_and_rendering(tmp_path: Path) -> None:
    write_dashboard_reports(tmp_path)
    overview = DashboardService(tmp_path).overview()
    executive = executive_summary(overview)
    assert executive["state"] in {"صالح للمتابعة", "يحتاج تحسين", "مرفوض بحثيا", "غير كاف للحكم"}
    assert executive["health"]["score"] >= 0
    assert executive["next_step"]

    templates_src = Path(__file__).resolve().parents[1] / "app" / "templates"
    static_src = Path(__file__).resolve().parents[1] / "app" / "static"
    app_dir = tmp_path / "app"
    app_dir.mkdir(exist_ok=True)
    import shutil

    shutil.copytree(templates_src, app_dir / "templates")
    shutil.copytree(static_src, app_dir / "static")
    response = TestClient(create_dashboard_app(tmp_path)).get("/")
    assert response.status_code == 200
    text = response.text
    assert "درجة الجاهزية البحثية" in text
    assert "الخطوة التالية المقترحة" in text
    assert "2026-01-01T00:00:00+00:00" not in text


def test_dashboard_css_has_overflow_guards() -> None:
    css = (Path(__file__).resolve().parents[1] / "app/static/dashboard/dashboard.css").read_text(
        encoding="utf-8"
    )
    assert "overflow-x: hidden" in css
    assert "minmax(0, 1fr)" in css
    assert "min-width: 0" in css
    assert ".table-wrap" in css and "overflow-x: auto" in css
