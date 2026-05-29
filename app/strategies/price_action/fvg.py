"""Fair value gap research detection."""

from dataclasses import dataclass

from app.data.models import Candle
from app.strategies.research.models import EvidenceDirection


@dataclass(frozen=True)
class FairValueGap:
    """Simple three-candle fair value gap."""

    direction: EvidenceDirection
    start_index: int
    end_index: int
    lower: float
    upper: float
    size: float

    @property
    def detected(self) -> bool:
        """Return True when the gap has positive size."""
        return self.size > 0


def detect_fair_value_gaps(
    candles: tuple[Candle, ...],
    minimum_size: float = 0.00005,
) -> tuple[FairValueGap, ...]:
    """Detect basic bullish and bearish three-candle FVGs."""
    gaps: list[FairValueGap] = []
    for index in range(2, len(candles)):
        first = candles[index - 2]
        third = candles[index]
        if third.low > first.high:
            size = third.low - first.high
            if size >= minimum_size:
                gaps.append(
                    FairValueGap(
                        EvidenceDirection.BULLISH,
                        index - 2,
                        index,
                        first.high,
                        third.low,
                        size,
                    )
                )
        if third.high < first.low:
            size = first.low - third.high
            if size >= minimum_size:
                gaps.append(
                    FairValueGap(
                        EvidenceDirection.BEARISH,
                        index - 2,
                        index,
                        third.high,
                        first.low,
                        size,
                    )
                )
    return tuple(gaps)


def latest_fvg(
    candles: tuple[Candle, ...],
    minimum_size: float = 0.00005,
) -> FairValueGap | None:
    """Return latest detected FVG."""
    gaps = detect_fair_value_gaps(candles, minimum_size)
    return gaps[-1] if gaps else None
