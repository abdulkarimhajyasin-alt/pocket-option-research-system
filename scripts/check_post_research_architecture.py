"""Validate post-research strategic architecture outputs and safety boundaries."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.post_research_architecture.schemas import FORBIDDEN_SOURCE_TERMS  # noqa: E402
from app.post_research_architecture.service import PostResearchArchitectureService  # noqa: E402


def main() -> None:
    """Run post-research architecture compliance checks."""
    run = PostResearchArchitectureService(PROJECT_ROOT).run_full_post_research_architecture()
    module_dir = PROJECT_ROOT / "app" / "post_research_architecture"
    report_dir = PROJECT_ROOT / "reports" / "post_research_architecture"
    storage_dir = PROJECT_ROOT / "storage" / "post_research_architecture"
    required_modules = {
        "__init__.py",
        "models.py",
        "schemas.py",
        "roadmap.py",
        "gap_analysis.py",
        "boundaries.py",
        "execution_blueprint.py",
        "broker_blueprint.py",
        "risk_blueprint.py",
        "monitoring_blueprint.py",
        "governance_blueprint.py",
        "transition_plan.py",
        "diagnostics.py",
        "recommendations.py",
        "storage.py",
        "reports.py",
        "service.py",
    }
    required_storage = {
        "roadmap.json",
        "gap_analysis.json",
        "execution_blueprint.json",
        "broker_blueprint.json",
        "risk_blueprint.json",
        "monitoring_blueprint.json",
        "governance_blueprint.json",
        "transition_plan.json",
        "diagnostics.json",
        "recommendations.json",
        "summary.json",
    }
    required_reports = {
        "post_research_summary.json",
        "roadmap_report.json",
        "gap_analysis_report.json",
        "execution_blueprint_report.json",
        "broker_blueprint_report.json",
        "risk_blueprint_report.json",
        "monitoring_blueprint_report.json",
        "governance_blueprint_report.json",
        "transition_plan_report.json",
        "diagnostics_report.json",
        "recommendations_report.json",
    }
    client = TestClient(create_dashboard_app(PROJECT_ROOT))
    responses = {
        "page": client.get("/post-research-architecture"),
        "root": client.get("/api/post-research-architecture"),
        "roadmap": client.get("/api/post-research-architecture/roadmap"),
        "gaps": client.get("/api/post-research-architecture/gaps"),
        "blueprints": client.get("/api/post-research-architecture/blueprints"),
        "transition": client.get("/api/post-research-architecture/transition"),
        "diagnostics": client.get("/api/post-research-architecture/diagnostics"),
        "recommendations": client.get("/api/post-research-architecture/recommendations"),
    }
    module_text = "\n".join(
        path.read_text(encoding="utf-8") for path in module_dir.glob("*.py")
    ).lower()
    checks = {
        "module_exists": module_dir.exists(),
        "required_module_files": required_modules.issubset(
            {path.name for path in module_dir.glob("*.py")}
        ),
        "required_scripts": all(
            (PROJECT_ROOT / "scripts" / name).exists()
            for name in (
                "run_post_research_architecture.py",
                "check_post_research_architecture.py",
            )
        ),
        "required_tests": (PROJECT_ROOT / "tests" / "test_post_research_architecture.py").exists(),
        "dashboard_template": (
            PROJECT_ROOT / "app" / "templates" / "dashboard" / "post_research_architecture.html"
        ).exists(),
        "reports": required_reports.issubset({path.name for path in report_dir.glob("*.json")}),
        "storage": required_storage.issubset({path.name for path in storage_dir.glob("*.json")}),
        "json_valid": all(
            _valid_json(path)
            for path in list(report_dir.glob("*.json")) + list(storage_dir.glob("*.json"))
        ),
        "summary_architecture_only": run.summary.get("architecture_only") is True,
        "summary_research_only": run.summary.get("research_only") is True,
        "no_forbidden_artifacts": not any(term in module_text for term in FORBIDDEN_SOURCE_TERMS),
        "dashboard_route": responses["page"].status_code == 200,
        "api_routes": all(response.status_code == 200 for response in responses.values()),
        "arabic_labels": "الهندسة الاستراتيجية لما بعد منصة البحث" in responses["page"].text,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


def _valid_json(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return True


if __name__ == "__main__":
    main()
