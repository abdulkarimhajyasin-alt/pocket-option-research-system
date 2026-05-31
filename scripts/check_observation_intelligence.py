"""Diagnostics for unified observation intelligence."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.observation_intelligence.service import ObservationIntelligenceService  # noqa: E402


def main() -> None:
    """Run observation intelligence compliance checks."""
    run = ObservationIntelligenceService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/observation-intelligence")
    api_response = client.get("/api/observation-intelligence")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/observation_intelligence.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "observation_summary.json",
        "quality_report.json",
        "confidence_report.json",
        "validation_report.json",
        "coverage_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "observation_intelligence"
    metadata = run.result.metadata
    checks = {
        "observations": len(run.result.observations) >= 4,
        "normalization": 0 <= run.result.normalization.score <= 100,
        "aggregation": 0 <= run.result.aggregation.score <= 100,
        "validation": 0 <= run.result.validation.score <= 100,
        "confidence": 0 <= run.result.confidence.score <= 100,
        "quality": 0 <= run.result.quality.score <= 100,
        "intelligence": 0 <= run.result.intelligence.score <= 100,
        "storage": all(Path(path).exists() for path in run.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "مركز ذكاء المراقبة",
                "عدد الملاحظات",
                "توزيع المصادر",
                "تضارب البيانات",
            )
        )
        and "Observation Intelligence" not in template_text,
        "observation_only": metadata.get("observation_only") is True,
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
