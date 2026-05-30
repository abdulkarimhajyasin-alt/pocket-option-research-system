from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.strategy_benchmark.comparator import StrategyComparator
from app.strategy_benchmark.profiles import default_benchmark_profiles
from app.strategy_benchmark.scoring import BenchmarkScoringEngine
from app.strategy_benchmark.service import StrategyBenchmarkService


def _inputs() -> dict:
    return {
        "signal_summary": {"average_quality": 72, "total_signals": 120},
        "performance_summary": {
            "stability_score": 68,
            "confidence_accuracy": 74,
        },
        "opportunity_summary": {"average_score": 70},
        "timeframe_summary": {"average_confirmation": 65},
        "confluence_summary": {"average_confluence": 62},
        "lifecycle_summary": {"average_quality": 66, "total_lifecycles": 100},
        "readiness_summary": {"readiness_score": 71, "stability_score": 69},
    }


def test_benchmark_profiles_and_scores_are_bounded():
    comparisons = StrategyComparator().compare(default_benchmark_profiles(), _inputs())
    scores = tuple(BenchmarkScoringEngine().score(item) for item in comparisons)
    assert len(comparisons) == 5
    assert len(scores) == 5
    assert all(0 <= item.score <= 100 for item in scores)
    assert {item.profile.profile_id for item in comparisons} >= {"current", "balanced"}


def test_strategy_benchmark_service_generates_outputs():
    run = StrategyBenchmarkService(Path(".")).run()
    assert len(run.result.rankings) == 5
    assert run.result.metadata["not_execution"] is True
    assert run.result.to_dict()["not_investment_advice"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_strategy_benchmark_dashboard_and_api_are_arabic():
    StrategyBenchmarkService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/strategy-benchmark")
    api = client.get("/api/strategy-benchmark")
    assert page.status_code == 200
    assert api.status_code == 200
    assert "مقارنة الاستراتيجيات" in page.text
    assert "أفضل ملف استراتيجي" in page.text
    assert "Strategy Benchmark" not in page.text
