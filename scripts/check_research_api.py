"""Diagnostics for the unified local research API."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.research_api.schemas import SNAPSHOT_KEYS  # noqa: E402
from app.research_api.service import UnifiedResearchAPIService  # noqa: E402


def main() -> None:
    """Run unified research API compliance checks."""
    service = UnifiedResearchAPIService(PROJECT_ROOT)
    run = service.run()
    snapshot = run.snapshot.to_dict()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    responses = {
        "page": client.get("/research-api"),
        "research": client.get("/api/research"),
        "signals": client.get("/api/research/signals"),
        "opportunities": client.get("/api/research/opportunities"),
        "paper": client.get("/api/research/paper"),
        "readiness": client.get("/api/research/readiness"),
        "knowledge_graph": client.get("/api/research/knowledge-graph"),
        "diagnostics": client.get("/api/research/diagnostics"),
    }
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/research_api.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "research_summary.json",
        "signal_intelligence_view.json",
        "opportunity_view.json",
        "paper_trading_view.json",
        "readiness_view.json",
        "knowledge_graph_summary.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    required_storage = {
        "unified_research_snapshot.json",
        "signal_intelligence_view.json",
        "opportunity_view.json",
        "paper_trading_view.json",
        "readiness_view.json",
        "knowledge_graph_summary.json",
        "diagnostics.json",
        "recommendations.json",
        "arabic_labels.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "research_api"
    storage_dir = PROJECT_ROOT / "storage" / "research_api"
    second_snapshot = UnifiedResearchAPIService(PROJECT_ROOT).snapshot().to_dict()
    checks = {
        "routes": all(response.status_code == 200 for response in responses.values()),
        "schema": tuple(snapshot.keys()) == SNAPSHOT_KEYS,
        "deterministic": snapshot == second_snapshot,
        "research_only": snapshot["metadata"].get("research_only") is True,
        "local_only": snapshot["metadata"].get("local_only") is True,
        "not_execution": snapshot["metadata"].get("not_execution") is True,
        "not_real_execution": snapshot["metadata"].get("not_real_execution") is True,
        "not_order_placement": snapshot["metadata"].get("not_order_placement") is True,
        "not_broker_access": snapshot["metadata"].get("not_broker_access") is True,
        "not_broker_api": snapshot["metadata"].get("not_broker_api") is True,
        "not_authentication": snapshot["metadata"].get("not_authentication") is True,
        "not_credential_handling": snapshot["metadata"].get("not_credential_handling") is True,
        "not_browser_automation": snapshot["metadata"].get("not_browser_automation") is True,
        "not_real_money": snapshot["metadata"].get("not_real_money") is True,
        "not_live_trading": snapshot["metadata"].get("not_live_trading") is True,
        "not_external_execution_adapter": (
            snapshot["metadata"].get("not_external_execution_adapter") is True
        ),
        "not_trading_automation": snapshot["metadata"].get("not_trading_automation") is True,
        "storage_paths": all(Path(path).exists() for path in run.storage_paths.values()),
        "report_paths": all(Path(path).exists() for path in run.report_paths.values()),
        "storage_files": required_storage.issubset(
            {path.name for path in storage_dir.glob("*.json")}
        ),
        "report_files": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "arabic": all(
            label in (template_text + responses["page"].text)
            for label in (
                "واجهة البحث الموحدة",
                "الإشارات",
                "الفرص",
                "الجاهزية",
                "خريطة المعرفة",
            )
        ),
        "api_payloads": all(
            response.json().get("metadata", {}).get("research_only") is True
            for key, response in responses.items()
            if key not in {"page", "research"}
        ),
        "root_payload": responses["research"].json().get("research_only") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
