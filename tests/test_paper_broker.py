"""Tests for local paper broker behavior."""

from datetime import UTC, datetime

from app.brokers.paper_broker import PaperBroker
from app.data.models import Candle
from app.signals.signal import SignalDirection, TradeSignal


def _candle(index: int, close: float) -> Candle:
    return Candle(
        symbol="EURUSD",
        timeframe="1m",
        timestamp=datetime(2026, 1, 1, 12, index, tzinfo=UTC),
        open=close,
        high=close + 0.0002,
        low=close - 0.0002,
        close=close,
    )


def _signal() -> TradeSignal:
    return TradeSignal(
        symbol="EURUSD",
        timeframe="1m",
        direction=SignalDirection.CALL,
        confidence=0.8,
        timestamp=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        strategy_name="test_strategy",
    )


def test_paper_broker_opens_and_settles_trade() -> None:
    broker = PaperBroker(initial_balance=100.0, payout_percentage=0.8, stake=10.0)
    broker.connect()
    opened = broker.place_trade(_signal(), _candle(0, 1.1000))
    settled = broker.settle_trade(opened["trade_id"], _candle(1, 1.1010))

    assert settled["outcome"] == "win"
    assert broker.get_balance() == 108.0
    assert len(broker.get_open_positions()) == 0
    assert len(broker.get_trade_history()) == 2
