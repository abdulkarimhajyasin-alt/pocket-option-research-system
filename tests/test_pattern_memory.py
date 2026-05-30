from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.pattern_memory.learning import AdaptiveLearningEngine
from app.pattern_memory.models import PatternMemoryRecord
from app.pattern_memory.pattern_engine import PatternDiscoveryEngine
from app.pattern_memory.scoring import PatternQualityEngine, PatternRankingEngine
from app.pattern_memory.service import PatternMemoryService
from app.pattern_memory.similarity import PatternSimilarityEngine


def _records() -> tuple[PatternMemoryRecord, ...]:
    return (
        PatternMemoryRecord(
            "one",
            "EURUSD",
            "جلسة لندن",
            "صاعد",
            "هيكل صاعد",
            "CISD صاعد مؤكد",
            "FVG صاعد",
            "IFVG غير موجود",
            "سحب سيولة",
            78,
            82,
            76,
            70,
            "WIN",
            "جودة بحثية عالية",
        ),
        PatternMemoryRecord(
            "two",
            "EURUSD",
            "جلسة لندن",
            "صاعد",
            "هيكل صاعد",
            "CISD صاعد مؤكد",
            "FVG صاعد",
            "IFVG غير موجود",
            "سحب سيولة",
            75,
            80,
            74,
            68,
            "WIN",
            "جودة بحثية عالية",
        ),
        PatternMemoryRecord(
            "three",
            "EURUSD",
            "جلسة لندن",
            "صاعد",
            "هيكل صاعد",
            "CISD صاعد مؤكد",
            "FVG صاعد",
            "IFVG غير موجود",
            "سحب سيولة",
            70,
            72,
            68,
            65,
            "LOSS",
            "جودة بحثية منخفضة",
        ),
    )


def test_pattern_memory_engines_are_bounded():
    records = _records()
    patterns = PatternDiscoveryEngine().discover(records)
    quality = PatternQualityEngine().evaluate(patterns)
    similarities = PatternSimilarityEngine().compare(records, patterns)
    insights = AdaptiveLearningEngine().learn(records, patterns)
    rankings = PatternRankingEngine().rank(records)
    assert patterns
    assert all(0 <= item.pattern_score <= 100 for item in patterns)
    assert all(0 <= item.score <= 100 for item in quality)
    assert len(similarities) == len(records)
    assert insights
    assert rankings


def test_pattern_memory_service_generates_outputs():
    run = PatternMemoryService(Path(".")).run()
    assert len(run.result.records) > 0
    assert run.result.metadata["not_execution"] is True
    assert run.result.to_dict()["not_investment_advice"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_pattern_memory_dashboard_and_api_are_arabic():
    PatternMemoryService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/pattern-memory")
    api = client.get("/api/pattern-memory")
    assert page.status_code == 200
    assert api.status_code == 200
    assert "محرك التعلم والأنماط" in page.text
    assert "أفضل نمط مكتشف" in page.text
    assert "Pattern Memory" not in page.text
