"""Diagnostics for research certification."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.research_certification.service import ResearchCertificationService  # noqa: E402


def main() -> None:
    """Run research certification compliance checks."""
    run = ResearchCertificationService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/research-certification")
    api_response = client.get("/api/research-certification")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/research_certification.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "certification_summary.json",
        "requirements_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
        "maturity_report.json",
        "robustness_report.json",
        "consistency_report.json",
        "stability_report.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "research_certification"
    checks = {
        "score": 0 <= run.result.certification.score <= 100,
        "requirements": len(run.result.requirements.checks) == 7,
        "maturity": 0 <= run.result.maturity.score <= 100,
        "diagnostics": run.result.diagnostics is not None,
        "storage": all(Path(path).exists() for path in run.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "محرك الاعتماد البحثي",
                "شهادة الجاهزية البحثية",
                "درجة الاعتماد",
                "توزيع الاعتماد",
            )
        )
        and "Research Certification" not in template_text,
        "research_only": run.result.metadata.get("not_execution") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
