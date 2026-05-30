from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.trade_lifecycle.entry import EntryAnalysisEngine
from app.trade_lifecycle.expiry import ExpiryAnalysisEngine
from app.trade_lifecycle.lifecycle import LifecycleQualityEngine
from app.trade_lifecycle.service import TradeLifecycleService
from app.trade_lifecycle.state_machine import LifecycleStateMachine


def _decision() -> dict:
    return {
        "opportunity_id": "research-1",
        "asset": "EURUSD",
        "classification": "تصنيف صعودي",
        "confluence_score": 76.0,
        "readiness": "جاهزة للأبحاث المتقدمة",
        "confluence": {
            "timestamp": "2026-05-30T10:00:00",
            "factors": [
                {
                    "name": "عامل الإشارة",
                    "score": 72,
                    "metrics": {"signal_confidence": 74},
                },
                {
                    "name": "عامل الأداء",
                    "score": 68,
                    "metrics": {},
                },
                {
                    "name": "عامل الفرصة",
                    "score": 73,
                    "metrics": {"opportunity_score": 70},
                },
                {
                    "name": "عامل الأطر الزمنية",
                    "score": 71,
                    "metrics": {"alignment_score": 69},
                },
                {
                    "name": "عامل الجلسة",
                    "score": 66,
                    "metrics": {"session_quality": 64},
                },
                {
                    "name": "عامل السيولة",
                    "score": 67,
                    "metrics": {"liquidity_score": 65},
                },
            ],
        },
        "rejection_reasons": [],
        "risk_factors": [],
    }


def test_lifecycle_stage_engines_are_bounded():
    decision = _decision()
    entry = EntryAnalysisEngine().evaluate(decision)
    expiry = ExpiryAnalysisEngine().evaluate(decision, entry.readiness_score)
    quality = LifecycleQualityEngine().evaluate(
        lifecycle_score=70,
        confluence_score=76,
        confirmation_quality=69,
        performance_quality=68,
    )
    assert 0 <= entry.readiness_score <= 100
    assert expiry.expiry in ExpiryAnalysisEngine.SUPPORTED_EXPIRIES
    assert quality.readiness != ""


def test_state_machine_tracks_transitions():
    from datetime import datetime

    state = LifecycleStateMachine().build("WIN", datetime(2026, 5, 30), False)
    assert state.current == "ناجحة"
    assert len(state.transitions) >= 5


def test_trade_lifecycle_service_generates_reports():
    result = TradeLifecycleService(Path(".")).run()
    assert result.records
    first = result.records[0]
    assert first.metadata["not_execution"] is True
    assert first.to_dict()["not_investment_advice"] is True
    assert all(Path(path).exists() for path in result.storage_paths.values())
    assert all(Path(path).exists() for path in result.report_paths.values())


def test_trade_lifecycle_dashboard_and_api_are_arabic():
    TradeLifecycleService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/trade-lifecycle")
    api = client.get("/api/trade-lifecycle")
    assert page.status_code == 200
    assert api.status_code == 200
    assert "دورة حياة الفرص" in page.text
    assert "أفضل فرصة مكتملة" in page.text
    assert "Trade Lifecycle" not in page.text
