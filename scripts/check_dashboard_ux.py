"""Phase 19 dashboard UX diagnostics."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.decision import executive_summary, health_score, research_decision  # noqa: E402
from app.dashboard.formatting import format_datetime, format_number, format_percent  # noqa: E402
from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.dashboard.service import DashboardService  # noqa: E402


def main() -> None:
    """Run deterministic dashboard UX diagnostics."""
    service = DashboardService(PROJECT_ROOT)
    overview = service.overview()
    app = create_dashboard_app(PROJECT_ROOT)
    route_paths = {route.path for route in app.routes}
    templates = [
        PROJECT_ROOT / "app/templates/dashboard/overview.html",
        PROJECT_ROOT / "app/templates/dashboard/datasets.html",
        PROJECT_ROOT / "app/templates/dashboard/validation.html",
        PROJECT_ROOT / "app/templates/dashboard/strategies.html",
        PROJECT_ROOT / "app/templates/dashboard/execution.html",
    ]
    css = (PROJECT_ROOT / "app/static/dashboard/dashboard.css").read_text(encoding="utf-8")
    overview_template = templates[0].read_text(encoding="utf-8")
    decision = research_decision(overview)
    health = health_score(overview)
    executive = executive_summary(overview)
    decision_labels = {
        "صالح للمتابعة",
        "يحتاج تحسين",
        "مرفوض بحثيا",
        "غير كاف للحكم",
    }
    decision_text = (PROJECT_ROOT / "app/dashboard/decision.py").read_text(
        encoding="utf-8"
    )
    checks = {
        "formatting_loads": (
            format_percent(100.0) == "100%"
            and format_number(2.599999999999998) == "2.60"
        ),
        "datetime_formatting": "T" not in format_datetime("2026-05-29T19:42:00+00:00"),
        "decision_engine": decision.status in decision_labels,
        "health_score": 0 <= health.score <= 100 and bool(health.label),
        "templates_present": all(path.exists() for path in templates),
        "routes_present": {
            "/",
            "/datasets",
            "/validation",
            "/strategies",
            "/execution",
        }.issubset(route_paths),
        "overview_panel": "درجة الجاهزية البحثية" in overview_template,
        "no_overview_iso_literal": "T00:00:00" not in overview_template,
        "overflow_guards": all(
            needle in css
            for needle in (
                "overflow-x: hidden",
                "min-width: 0",
                "minmax(0, 1fr)",
                "overflow-x: auto",
            )
        ),
        "arabic_status_labels": all(
            label in (overview_template + decision_text)
            for label in decision_labels
        ),
        "executive_payload": bool(executive["reason"] and executive["next_step"]),
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
