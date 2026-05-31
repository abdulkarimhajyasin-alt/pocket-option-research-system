"""Diagnostics for production research architecture audit."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.architecture_audit.service import ArchitectureAuditService  # noqa: E402
from app.dashboard.routes import create_dashboard_app  # noqa: E402


def main() -> None:
    """Run architecture audit compliance checks."""
    run = ArchitectureAuditService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/architecture-audit")
    api_response = client.get("/api/architecture-audit")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/architecture_audit.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "architecture_summary.json",
        "consistency_report.json",
        "dependency_report.json",
        "performance_report.json",
        "safety_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
        "final_certification.json",
    }
    required_storage = {
        "audit_results.json",
        "consistency_results.json",
        "dependency_results.json",
        "performance_results.json",
        "safety_results.json",
        "diagnostics.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "architecture_audit"
    storage_dir = PROJECT_ROOT / "storage" / "architecture_audit"
    metadata = run.result.metadata
    cert = run.result.certification
    checks = {
        "architecture": 0 <= cert.architecture_score <= 100,
        "consistency": 0 <= cert.consistency_score <= 100,
        "dependency": 0 <= cert.dependency_score <= 100,
        "performance": 0 <= cert.performance_score <= 100,
        "safety": 0 <= cert.safety_score <= 100,
        "overall": 0 <= cert.overall_score <= 100,
        "diagnostics": len(run.result.diagnostics) >= 1,
        "recommendations": len(run.result.recommendations) >= 1,
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
                "التدقيق النهائي للمنصة",
                "تدقيق المنصة",
                "درجة المعمارية",
                "درجة الاتساق",
                "درجة السلامة",
                "حالة الاعتماد النهائي",
            )
        )
        and "Architecture Audit" not in template_text,
        "architecture_audit_only": metadata.get("architecture_audit_only") is True,
        "hardening_only": metadata.get("hardening_only") is True,
        "research_only": metadata.get("research_only") is True,
        "not_execution": metadata.get("not_execution") is True,
        "not_real_execution": metadata.get("not_real_execution") is True,
        "not_broker_access": metadata.get("not_broker_access") is True,
        "not_broker_api": metadata.get("not_broker_api") is True,
        "not_account_login": metadata.get("not_account_login") is True,
        "not_authentication": metadata.get("not_authentication") is True,
        "not_credential_handling": metadata.get("not_credential_handling") is True,
        "not_browser_automation": metadata.get("not_browser_automation") is True,
        "not_real_money": metadata.get("not_real_money") is True,
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
