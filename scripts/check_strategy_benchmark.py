"""Diagnostics for strategy benchmark research."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.strategy_benchmark.service import StrategyBenchmarkService  # noqa: E402


def main() -> None:
    """Run strategy benchmark compliance checks."""
    run = StrategyBenchmarkService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/strategy-benchmark")
    api_response = client.get("/api/strategy-benchmark")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/strategy_benchmark.html"
    ).read_text(encoding="utf-8")
    required_reports = {
        "benchmark_summary.json",
        "profile_rankings.json",
        "improvement_analysis.json",
        "stability_analysis.json",
        "robustness_analysis.json",
        "recommendations_report.json",
    }
    report_dir = PROJECT_ROOT / "reports" / "strategy_benchmark"
    checks = {
        "profiles": len(run.result.comparisons) == 5,
        "scores": all(0 <= item.score <= 100 for item in run.result.scores),
        "rankings": len(run.result.rankings) == 5,
        "storage": all(Path(path).exists() for path in run.storage_paths.values()),
        "reports": required_reports.issubset(
            {path.name for path in report_dir.glob("*.json")}
        ),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "مقارنة الاستراتيجيات",
                "أفضل ملف استراتيجي",
                "ترتيب الملفات",
                "التوصيات",
            )
        )
        and "Strategy Benchmark" not in template_text,
        "research_only": run.result.metadata.get("not_execution") is True,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
