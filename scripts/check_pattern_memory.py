"""Diagnostics for adaptive pattern memory research."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.pattern_memory.service import PatternMemoryService  # noqa: E402


def main() -> None:
    """Run pattern memory compliance checks."""
    run = PatternMemoryService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/pattern-memory")
    api_response = client.get("/api/pattern-memory")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/pattern_memory.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "pattern_summary.json",
        "pattern_rankings.json",
        "pattern_quality.json",
        "similarity_analysis.json",
        "learning_analysis.json",
        "adaptation_analysis.json",
        "stability_analysis.json",
        "reliability_analysis.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "pattern_memory"
    checks = {
        "records": len(run.result.records) > 0,
        "patterns": len(run.result.discovered_patterns) > 0,
        "similarity": len(run.result.similarities) == len(run.result.records),
        "learning": len(run.result.learning_insights) > 0,
        "storage": all(Path(path).exists() for path in run.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "محرك التعلم والأنماط",
                "أفضل نمط مكتشف",
                "ترتيب الأنماط",
                "تقدم التعلم",
            )
        )
        and "Pattern Memory" not in template_text,
        "research_only": run.result.metadata.get("not_execution") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
