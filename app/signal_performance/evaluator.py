"""Historical outcome evaluator for research signals."""

from __future__ import annotations

from app.data.models import Candle
from app.signal_performance.models import PaperOutcome, SignalOutcome, TrackedSignal


class SignalOutcomeEvaluator:
    """Evaluate whether a research classification matched future candle movement."""

    def evaluate(
        self,
        signal: TrackedSignal,
        entry: Candle,
        future: Candle | None,
        candles_elapsed: int,
    ) -> SignalOutcome:
        if future is None:
            return SignalOutcome(
                signal_id=signal.signal_id,
                outcome=PaperOutcome.UNRESOLVED,
                candles_elapsed=0,
                evaluation_timestamp=entry.timestamp,
                evaluation_reason="لا توجد شموع لاحقة كافية للتقييم",
                outcome_score=0.0,
            )
        movement = future.close - entry.close
        if signal.classification == "تصنيف صعودي":
            outcome = self._directional_outcome(movement)
        elif signal.classification == "تصنيف هبوطي":
            outcome = self._directional_outcome(-movement)
        else:
            outcome = PaperOutcome.BREAKEVEN
        return SignalOutcome(
            signal_id=signal.signal_id,
            outcome=outcome,
            candles_elapsed=candles_elapsed,
            evaluation_timestamp=future.timestamp,
            evaluation_reason="تقييم تاريخي لحركة الشموع بعد التصنيف البحثي",
            outcome_score=self._score(outcome),
        )

    def _directional_outcome(self, movement: float) -> PaperOutcome:
        if movement > 0:
            return PaperOutcome.WIN
        if movement < 0:
            return PaperOutcome.LOSS
        return PaperOutcome.BREAKEVEN

    def _score(self, outcome: PaperOutcome) -> float:
        return {
            PaperOutcome.WIN: 1.0,
            PaperOutcome.LOSS: 0.0,
            PaperOutcome.BREAKEVEN: 0.5,
            PaperOutcome.UNRESOLVED: 0.0,
        }[outcome]
