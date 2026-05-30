from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.market_regime.detector import MarketRegimeDetector
from app.market_regime.models import RegimeCandle
from app.market_regime.service import MarketRegimeService
from app.market_regime.transition import TransitionDetectionEngine
from app.market_regime.trend import TrendStrengthEngine
from app.market_regime.volatility import VolatilityEngine


def _candles() -> tuple[RegimeCandle, ...]:
    rows = []
    price = 1.1000
    for index in range(20):
        open_price = price
        close = price + 0.0001
        high = close + 0.00005
        low = open_price - 0.00003
        rows.append(RegimeCandle(str(index), open_price, high, low, close, 100))
        price = close
    return tuple(rows)


def test_market_regime_engines_are_bounded():
    candles = _candles()
    volatility = VolatilityEngine().evaluate(candles)
    trend = TrendStrengthEngine().evaluate(candles)
    transition = TransitionDetectionEngine().evaluate(candles)
    regime = MarketRegimeDetector().classify(volatility, trend, transition)
    assert 0 <= volatility.score <= 100
    assert 0 <= trend.score <= 100
    assert 0 <= transition.frequency <= 100
    assert 0 <= regime.regime_score <= 100
    assert regime.regime_state


def test_market_regime_service_generates_outputs():
    run = MarketRegimeService(Path(".")).run()
    assert run.result.regime.regime_state
    assert run.result.metadata["not_execution"] is True
    assert run.result.to_dict()["not_investment_advice"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_market_regime_dashboard_and_api_are_arabic():
    MarketRegimeService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/market-regime")
    api = client.get("/api/market-regime")
    assert page.status_code == 200
    assert api.status_code == 200
    assert "محرك حالة السوق" in page.text
    assert "الوضع الحالي للسوق" in page.text
    assert "Market Regime" not in page.text
