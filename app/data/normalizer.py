"""Market data normalization utilities."""

from collections.abc import Iterable
from datetime import UTC

from loguru import logger

from app.data.models import Candle, CandleSeries


class MarketDataNormalizer:
    """Normalizes and validates candle collections."""

    TIMEFRAME_ALIASES = {
        "m1": "1m",
        "1min": "1m",
        "1minute": "1m",
        "m5": "5m",
        "5min": "5m",
        "5minute": "5m",
        "h1": "1h",
        "1hour": "1h",
    }

    def normalize_timeframe(self, timeframe: str) -> str:
        """Normalize timeframe aliases to a stable lowercase format."""
        normalized = timeframe.strip().lower()
        return self.TIMEFRAME_ALIASES.get(normalized, normalized)

    def normalize_candles(
        self,
        symbol: str,
        timeframe: str,
        candles: Iterable[Candle],
    ) -> CandleSeries:
        """Sort candles, normalize metadata, and remove duplicates."""
        normalized_timeframe = self.normalize_timeframe(timeframe)
        by_timestamp: dict[object, Candle] = {}
        duplicate_count = 0

        for candle in candles:
            timestamp = candle.timestamp.astimezone(UTC)
            normalized_candle = Candle(
                symbol=symbol.upper(),
                timeframe=normalized_timeframe,
                timestamp=timestamp,
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
            )

            if timestamp in by_timestamp:
                duplicate_count += 1
                logger.warning("Duplicate candle skipped at {}", timestamp.isoformat())
                continue

            by_timestamp[timestamp] = normalized_candle

        sorted_candles = sorted(by_timestamp.values(), key=lambda candle: candle.timestamp)
        if duplicate_count:
            logger.info("Skipped {} duplicate candles", duplicate_count)

        series = CandleSeries(
            symbol=symbol.upper(),
            timeframe=normalized_timeframe,
            candles=sorted_candles,
        )
        self.validate_ordering(series)
        logger.info("Normalized {} candles for {} {}", len(series), series.symbol, series.timeframe)
        return series

    def validate_ordering(self, series: CandleSeries) -> bool:
        """Validate chronological candle ordering."""
        previous = None
        for candle in series:
            if previous is not None and candle.timestamp <= previous:
                logger.error("Candle ordering validation failed at {}", candle.timestamp)
                return False
            previous = candle.timestamp
        return True
