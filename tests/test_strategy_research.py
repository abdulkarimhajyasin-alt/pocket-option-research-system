"""Tests for Phase 13 strategy research layer."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
import subprocess
import sys

from app.data.models import Candle
from app.signals.signal import SignalDirection
from app.strategies.base_strategy import StrategyParameters
from app.strategies.price_action.cisd import detect_cisd_displacement
from app.strategies.price_action.fvg import latest_fvg
from app.strategies.price_action.liquidity import detect_liquidity_sweep
from app.strategies.price_action.structure import (
    StructureDirection,
    detect_swing_highs,
    detect_swing_lows,
    market_structure_direction,
)
from app.strategies.registry import default_strategy_registry
from app.strategies.research.context import MarketContextBuilder
from app.strategies.research.filters import ResearchFilters
from app.strategies.research.models import EvidenceDirection, SignalEvidence
from app.strategies.research.scoring import EvidenceScorer, EvidenceScoringConfig
from app.strategies.research_cisd_fvg_strategy import ResearchCisdFvgStrategy


def _candle(index: int, open_price: float, high: float, low: float, close: float) -> Candle:
    return Candle(
        symbol="EURUSD",
        timeframe="1m",
        timestamp=datetime(2026, 1, 1, 1, 0, tzinfo=UTC) + timedelta(minutes=index),
        open=open_price,
        high=high,
        low=low,
        close=close,
        volume=100,
    )


def _research_history() -> tuple[Candle, ...]:
    candles = []
    price = 1.1000
    for index in range(22):
        close = price + 0.00003
        candles.append(_candle(index, price, close + 0.00004, price - 0.00004, close))
        price = close
    candles.append(_candle(22, 1.1007, 1.1008, 1.1006, 1.10075))
    candles.append(_candle(23, 1.10078, 1.1009, 1.10076, 1.10085))
    candles.append(_candle(24, 1.10105, 1.10145, 1.10101, 1.1014))
    return tuple(candles)


def test_market_context_tracks_session_and_state() -> None:
    """Market context exposes symbol, timeframe, session, trend, and volatility state."""
    context = MarketContextBuilder().from_candles(_research_history())

    assert context.market.symbol == "EURUSD"
    assert context.market.session == "asian"
    assert context.market.trend_state == "bullish"


def test_price_action_structure_detection() -> None:
    """Structure helpers detect swings and direction."""
    candles = (
        _candle(0, 1.0, 1.1, 0.9, 1.0),
        _candle(1, 1.0, 1.2, 0.95, 1.1),
        _candle(2, 1.1, 1.15, 0.92, 1.05),
        _candle(3, 1.05, 1.25, 1.0, 1.2),
        _candle(4, 1.2, 1.22, 1.05, 1.15),
        _candle(5, 1.15, 1.3, 1.1, 1.25),
    )

    assert detect_swing_highs(candles, lookback=1)
    assert detect_swing_lows(candles, lookback=1)
    assert market_structure_direction(_research_history()) == StructureDirection.BULLISH


def test_fvg_liquidity_and_cisd_detection() -> None:
    """Price-action modules detect FVG, sweep, and displacement."""
    history = _research_history()
    sweep_history = (
        _candle(0, 1.0, 1.1, 0.95, 1.05),
        _candle(1, 1.05, 1.11, 0.96, 1.08),
        _candle(2, 1.08, 1.12, 0.97, 1.09),
        _candle(3, 1.09, 1.13, 0.98, 1.1),
        _candle(4, 1.1, 1.14, 0.99, 1.11),
        _candle(5, 1.11, 1.16, 1.02, 1.10),
    )

    assert latest_fvg(history, minimum_size=0.00001) is not None
    assert detect_cisd_displacement(history, body_ratio_threshold=0.35) is not None
    sweep = detect_liquidity_sweep(sweep_history, lookback=5)
    assert sweep is not None
    assert sweep.direction == EvidenceDirection.BEARISH


def test_research_filters_and_evidence_scoring() -> None:
    """Filters and scoring return structured deterministic results."""
    candles = _research_history()
    filters = ResearchFilters(atr_period=3)
    evidence = (
        SignalEvidence("trend_alignment", EvidenceDirection.BULLISH, 0.8),
        SignalEvidence("fvg_presence", EvidenceDirection.BULLISH, 0.7),
        SignalEvidence("cisd_displacement", EvidenceDirection.BULLISH, 0.9),
    )

    assert filters.atr_between(candles, minimum=0.00001, maximum=0.01).passed
    assert filters.session_allowed("asian", ("asian",)).passed
    score = EvidenceScorer(
        EvidenceScoringConfig(minimum_evidence=3, confidence_threshold=0.5)
    ).score(evidence)

    assert score.direction == SignalDirection.CALL
    assert score.confidence >= 0.5


def test_research_strategy_generates_explainable_signal() -> None:
    """Research strategy emits a signal and records its decision explanation."""
    strategy = ResearchCisdFvgStrategy(
        StrategyParameters(
            confidence_threshold=0.55,
            symbols=("EURUSD",),
            timeframes=("1m",),
            values={
                "minimum_history": 10,
                "sessions": ("asian",),
                "atr_period": 3,
                "atr_minimum": 0.00001,
                "atr_maximum": 0.01,
                "minimum_body_ratio": 0.3,
                "minimum_range": 0.00001,
                "maximum_wick_ratio": 0.9,
                "minimum_evidence": 3,
                "cisd_body_ratio": 0.3,
                "cisd_range_multiple": 0.5,
                "fvg_minimum_size": 0.00001,
            },
        )
    )
    history = _research_history()

    signal = strategy.on_candle({"current_candle": history[-1], "history": history})

    assert signal is not None
    assert signal.direction == SignalDirection.CALL
    assert strategy.decisions[-1].generated_signal
    assert strategy.decisions[-1].evidence


def test_research_strategy_registry_integration() -> None:
    """Default registry can create the research strategy candidate."""
    strategy = default_strategy_registry().create(
        "research_cisd_fvg_strategy",
        parameters=StrategyParameters(symbols=("EURUSD",), timeframes=("1m",)),
    )

    assert strategy.name == "research_cisd_fvg_strategy"


def test_strategy_research_runner_behavior() -> None:
    """Research runner completes and prints required summary fields."""
    result = subprocess.run(
        [sys.executable, "scripts/run_strategy_research.py"],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert "total_signals" in result.stdout
    assert "evidence_summary" in result.stdout
