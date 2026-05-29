"""Deterministic synthetic dataset generation."""

from __future__ import annotations

import math
import random
from datetime import UTC, datetime, timedelta

from app.data.models import Candle, CandleSeries
from app.datasets.models import DatasetProfile
from app.datasets.normalization import DatasetNormalizer
from app.datasets.utils import parse_timeframe_seconds


class SyntheticDatasetGenerator:
    """Generate deterministic synthetic OHLCV datasets for testing and research."""

    def __init__(self, normalizer: DatasetNormalizer | None = None) -> None:
        self.normalizer = normalizer or DatasetNormalizer()

    def generate(
        self,
        profile: DatasetProfile,
        symbol: str = "EURUSD",
        timeframe: str = "1m",
        rows: int = 200,
        start: datetime | None = None,
        seed: int = 42,
    ) -> CandleSeries:
        """Generate a deterministic synthetic candle series."""
        rng = random.Random(seed)
        timestamp = start or datetime(2026, 1, 1, tzinfo=UTC)
        step = timedelta(seconds=parse_timeframe_seconds(timeframe))
        normalized_symbol = self.normalizer.normalize_symbol(symbol)
        normalized_timeframe = self.normalizer.normalize_timeframe(timeframe)
        price = 1.1000
        candles: list[Candle] = []
        for index in range(rows):
            movement = self._movement(profile, index, rng)
            open_price = price
            close = max(0.0001, open_price + movement)
            wick = abs(movement) * 0.6 + self._noise(profile, rng) * 0.2 + 0.00002
            high = max(open_price, close) + wick
            low = min(open_price, close) - wick
            candles.append(
                Candle(
                    symbol=normalized_symbol,
                    timeframe=normalized_timeframe,
                    timestamp=timestamp + index * step,
                    open=round(open_price, 6),
                    high=round(high, 6),
                    low=round(low, 6),
                    close=round(close, 6),
                    volume=round(100 + abs(movement) * 100000 + rng.random() * 10, 2),
                )
            )
            price = close
        return CandleSeries(normalized_symbol, normalized_timeframe, candles)

    def _movement(self, profile: DatasetProfile, index: int, rng: random.Random) -> float:
        if profile == DatasetProfile.TRENDING:
            return 0.00004 + rng.uniform(-0.000015, 0.000025)
        if profile == DatasetProfile.RANGING:
            return math.sin(index / 6.0) * 0.00005 + rng.uniform(-0.000015, 0.000015)
        if profile == DatasetProfile.VOLATILE:
            return rng.uniform(-0.00028, 0.00028)
        if profile == DatasetProfile.LOW_VOLATILITY:
            return rng.uniform(-0.000015, 0.000015)
        return rng.uniform(-0.0001, 0.0001) + math.sin(index / 3.0) * 0.00003

    def _noise(self, profile: DatasetProfile, rng: random.Random) -> float:
        if profile == DatasetProfile.VOLATILE:
            return rng.uniform(0.00004, 0.00018)
        if profile == DatasetProfile.LOW_VOLATILITY:
            return rng.uniform(0.000005, 0.00002)
        return rng.uniform(0.00001, 0.00006)
