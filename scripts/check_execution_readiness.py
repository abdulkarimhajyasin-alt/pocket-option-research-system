"""Diagnostics for the research-only execution readiness framework."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.execution_readiness.models import FAIL, PASS, WARNING  # noqa: E402
from app.execution_readiness.service import ExecutionReadinessService  # noqa: E402


def main() -> None:
    """Run execution-readiness compliance checks."""
    run = ExecutionReadinessService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/execution-readiness")
    api_response = client.get("/api/execution-readiness")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/execution_readiness.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "execution_summary.json",
        "readiness_report.json",
        "qualification_report.json",
        "gate_report.json",
        "validation_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    required_storage = {
        "execution_candidates.json",
        "readiness_results.json",
        "qualification_results.json",
        "gate_results.json",
        "validation_results.json",
        "diagnostics.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "execution_readiness"
    storage_dir = PROJECT_ROOT / "storage" / "execution_readiness"
    metadata = run.result.metadata
    checks = {
        "candidates": len(run.result.candidates) >= 5,
        "readiness": 0 <= run.result.readiness.score <= 100,
        "qualification": 0 <= run.result.qualification.score <= 100,
        "gates": all(gate.state in {PASS, WARNING, FAIL} for gate in run.result.gates),
        "scoring": 0 <= run.result.scoring.readiness_score <= 100,
        "validation": 0 <= run.result.validation.score <= 100,
        "storage_paths": all(Path(path).exists() for path in run.storage_paths.values()),
        "report_paths": all(Path(path).exists() for path in run.report_paths.values()),
        "storage_files": required_storage.issubset(
            {path.name for path in storage_dir.glob("*.json")}
        ),
        "report_files": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "إطار جاهزية التنفيذ",
                "جاهزية التنفيذ",
                "عدد المرشحين",
                "توزيع الجاهزية",
                "نتائج البوابات",
            )
        )
        and "Execution Readiness" not in template_text,
        "research_only": metadata.get("research_only") is True,
        "readiness_only": metadata.get("readiness_only") is True,
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
