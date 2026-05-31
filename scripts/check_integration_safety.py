"""Diagnostics for the external integration safety boundary."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.integration_safety.models import (  # noqa: E402
    ALLOWED_CAPABILITIES,
    FORBIDDEN_CAPABILITIES,
)
from app.integration_safety.service import IntegrationSafetyService  # noqa: E402


def main() -> None:
    """Run integration safety compliance checks."""
    run = IntegrationSafetyService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/integration-safety")
    api_response = client.get("/api/integration-safety")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/integration_safety.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "safety_summary.json",
        "boundary_report.json",
        "permission_report.json",
        "restriction_report.json",
        "compliance_report.json",
        "audit_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    required_storage = {
        "safety_policy.json",
        "boundary_results.json",
        "permission_results.json",
        "restriction_results.json",
        "compliance_results.json",
        "audit_records.json",
        "diagnostics.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "integration_safety"
    storage_dir = PROJECT_ROOT / "storage" / "integration_safety"
    metadata = run.result.metadata
    policy = run.result.policy
    checks = {
        "policy": 0 <= policy.safety_score <= 100,
        "compliance": 0 <= policy.compliance_score <= 100,
        "permissions": run.result.permissions.get("permission_score") == 100.0,
        "restrictions": run.result.restrictions.get("restriction_score") == 100.0,
        "no_violations": run.result.restrictions.get("violations") == [],
        "allowed": tuple(policy.allowed_capabilities) == ALLOWED_CAPABILITIES,
        "forbidden": tuple(policy.forbidden_capabilities) == FORBIDDEN_CAPABILITIES,
        "audit": bool(run.result.audit.get("audit_id")),
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
                "حدود أمان التكامل الخارجي",
                "أمان التكامل",
                "توزيع السلامة",
                "توزيع الامتثال",
                "القدرات المسموحة",
                "القدرات المحظورة",
                "سجل التدقيق",
            )
        )
        and "External Integration" not in template_text,
        "safety_boundary_only": metadata.get("safety_boundary_only") is True,
        "readiness_only": metadata.get("readiness_only") is True,
        "research_only": metadata.get("research_only") is True,
        "not_execution": metadata.get("not_execution") is True,
        "not_real_execution": metadata.get("not_real_execution") is True,
        "not_order_placement": metadata.get("not_order_placement") is True,
        "not_broker_access": metadata.get("not_broker_access") is True,
        "not_broker_api": metadata.get("not_broker_api") is True,
        "not_account_login": metadata.get("not_account_login") is True,
        "not_authentication": metadata.get("not_authentication") is True,
        "not_credential_handling": metadata.get("not_credential_handling") is True,
        "not_browser_automation": metadata.get("not_browser_automation") is True,
        "not_real_money": metadata.get("not_real_money") is True,
        "not_position_management": metadata.get("not_position_management") is True,
        "not_live_trading": metadata.get("not_live_trading") is True,
        "not_external_execution_adapter": (
            metadata.get("not_external_execution_adapter") is True
        ),
        "not_trading_automation": metadata.get("not_trading_automation") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
