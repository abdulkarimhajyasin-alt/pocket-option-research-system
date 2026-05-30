"""Research-only paper evaluation engine."""

from __future__ import annotations

from app.data.models import CandleSeries
from app.signal_performance.evaluator import SignalOutcomeEvaluator
from app.signal_performance.models import PaperTradeResult, TrackedSignal


class PaperTradingEngine:
    """Evaluate signal outcomes using historical candles only."""

    def __init__(self, horizon_candles: int = 3) -> None:
        self.horizon_candles = horizon_candles
        self.evaluator = SignalOutcomeEvaluator()

    def evaluate(
        self,
        signals: list[TrackedSignal],
        candles: CandleSeries,
    ) -> list[PaperTradeResult]:
        by_time = {candle.timestamp: index for index, candle in enumerate(candles)}
        results = []
        for signal in signals:
            index = by_time.get(signal.timestamp)
            if index is None:
                continue
            entry = candles[index]
            future_index = index + self.horizon_candles
            future = candles[future_index] if future_index < len(candles) else None
            outcome = self.evaluator.evaluate(
                signal,
                entry,
                future,
                self.horizon_candles if future is not None else 0,
            )
            evaluation_price = future.close if future is not None else entry.close
            results.append(
                PaperTradeResult(
                    signal=signal,
                    outcome=outcome,
                    entry_price=entry.close,
                    evaluation_price=evaluation_price,
                    movement=round(evaluation_price - entry.close, 8),
                )
            )
        return results
