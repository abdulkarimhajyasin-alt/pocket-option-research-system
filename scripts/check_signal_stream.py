"""Diagnostics for the research-only signal stream engine."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.signal_stream.service import SignalStreamService  # noqa: E402


def main() -> None:
    """Run signal stream compliance checks."""
    run = SignalStreamService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/signal-stream")
    api_response = client.get("/api/signal-stream")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/signal_stream.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "signal_summary.json",
        "stream_report.json",
        "quality_report.json",
        "readiness_report.json",
        "validation_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "signal_stream"
    metadata = run.result.metadata
    directions = {item.direction.value for item in run.result.stream.events}
    checks = {
        "signals": len(run.result.stream.events) >= 5,
        "directions": directions.issubset({"CALL", "PUT", "NO_TRADE"}),
        "stream": 0 <= run.result.stream.score <= 100,
        "queue": 0 <= run.result.queue.score <= 100,
        "timeline": 0 <= run.result.timeline.score <= 100,
        "scoring": 0 <= run.result.scoring.score <= 100,
        "validation": 0 <= run.result.validation.score <= 100,
        "storage": all(Path(path).exists() for path in run.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "محرك تدفق الإشارات",
                "عدد الإشارات",
                "توزيع الإشارات",
                "كثافة الإشارات",
            )
        )
        and "Signal Stream" not in template_text,
        "research_only": metadata.get("research_only") is True,
        "not_execution": metadata.get("not_execution") is True,
        "not_order_placement": metadata.get("not_order_placement") is True,
        "not_account_login": metadata.get("not_account_login") is True,
        "not_broker_authentication": metadata.get("not_broker_authentication") is True,
        "not_credential_handling": metadata.get("not_credential_handling") is True,
        "not_browser_automation": metadata.get("not_browser_automation") is True,
        "not_broker_control": metadata.get("not_broker_control") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
