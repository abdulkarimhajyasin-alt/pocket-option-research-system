"""CISD-like candle displacement research utilities."""

from dataclasses import dataclass

from app.data.models import Candle
from app.strategies.research.models import EvidenceDirection


@dataclass(frozen=True)
class CisdDisplacement:
    """Candle displacement resembling a change in state of delivery."""

    direction: EvidenceDirection
    index: int
    body_ratio: float
    range_multiple: float
    detected: bool = True


def detect_cisd_displacement(
    candles: tuple[Candle, ...],
    lookback: int = 5,
    body_ratio_threshold: float = 0.55,
    range_multiple_threshold: float = 1.2,
) -> CisdDisplacement | None:
    """Detect latest candle displacement against recent average range."""
    if len(candles) < lookback + 1:
        return None
    current = candles[-1]
    prior = candles[-lookback - 1 : -1]
    current_range = max(current.high - current.low, 0.0000001)
    average_range = sum(candle.high - candle.low for candle in prior) / len(prior)
    body_ratio = abs(current.close - current.open) / current_range
    range_multiple = current_range / max(average_range, 0.0000001)
    if body_ratio < body_ratio_threshold or range_multiple < range_multiple_threshold:
        return None
    direction = (
        EvidenceDirection.BULLISH if current.close > current.open else EvidenceDirection.BEARISH
    )
    return CisdDisplacement(
        direction=direction,
        index=len(candles) - 1,
        body_ratio=body_ratio,
        range_multiple=range_multiple,
    )
