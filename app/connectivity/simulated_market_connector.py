"""Simulated external market connector with no network access."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from random import Random
from time import perf_counter, sleep
from typing import Any

import yaml
from loguru import logger

from app.connectivity.base_connector import BaseReadOnlyConnector
from app.connectivity.models import ConnectorCapabilities
from app.data.models import Candle, CandleSeries


class SimulatedMarketConnector(BaseReadOnlyConnector):
    """Read-only connector that simulates external market data locally."""

    name = "simulated_market_connector"

    def __init__(
        self,
        capabilities: ConnectorCapabilities,
        latency_ms: float = 0.0,
        seed: int = 7,
    ) -> None:
        super().__init__(capabilities)
        self.latency_ms = latency_ms
        self.random = Random(seed)

    @classmethod
    def from_yaml(cls, path: Path | str) -> "SimulatedMarketConnector":
        """Create a simulated connector from YAML config."""
        config_path = Path(path)
        raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        capabilities = ConnectorCapabilities(
            market_data_read=bool(raw.get("market_data_read", True)),
            historical_data_read=bool(raw.get("historical_data_read", True)),
            account_info_read=bool(raw.get("account_info_read", False)),
            trade_execution_enabled=bool(raw.get("trade_execution_enabled", False)),
            supported_symbols=tuple(raw.get("symbols", [])),
            supported_timeframes=tuple(raw.get("timeframes", [])),
            supported_data_modes=tuple(
                raw.get("data_modes", ["historical", "latest", "simulated"])
            ),
        )
        return cls(
            capabilities=capabilities,
            latency_ms=float(raw.get("latency_ms", 0.0)),
            seed=int(raw.get("seed", 7)),
        )

    def connect(self) -> None:
        """Simulate connector startup."""
        self.validate_environment()
        latency = self._simulate_latency()
        self._health.mark_connected(latency)
        logger.bind(component="connectivity").info("Simulated connector connected")

    def disconnect(self) -> None:
        """Simulate connector shutdown."""
        self._health.mark_disconnected()
        logger.bind(component="connectivity").info("Simulated connector disconnected")

    def ping(self) -> Any:
        """Run a simulated heartbeat."""
        latency = self._simulate_latency()
        self._health.mark_connected(latency)
        logger.bind(component="connectivity").info("Simulated connector heartbeat")
        return self._health

    def fetch_latest_candles(self, symbol: str, timeframe: str, limit: int) -> CandleSeries:
        """Fetch latest simulated candles."""
        return self.fetch_historical_candles(symbol, timeframe, limit=limit)

    def fetch_historical_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int | None = None,
    ) -> CandleSeries:
        """Generate a deterministic batch of realistic local candles."""
        self.assert_market_supported(symbol, timeframe)
        count = limit or 100
        interval = timedelta(minutes=5 if timeframe.lower() == "5m" else 1)
        end_time = datetime.now(tz=UTC).replace(second=0, microsecond=0)
        start_time = end_time - interval * (count - 1)
        price = 1.1000
        candles: list[Candle] = []
        self._simulate_latency()
        for index in range(count):
            timestamp = start_time + interval * index
            drift = self.random.uniform(-0.00035, 0.00035)
            open_price = price
            close_price = max(0.0001, open_price + drift)
            high = max(open_price, close_price) + self.random.uniform(0.00002, 0.00018)
            low = min(open_price, close_price) - self.random.uniform(0.00002, 0.00018)
            candles.append(
                Candle(
                    symbol=symbol.upper(),
                    timeframe=timeframe.lower(),
                    timestamp=timestamp,
                    open=round(open_price, 5),
                    high=round(high, 5),
                    low=round(low, 5),
                    close=round(close_price, 5),
                    volume=round(self.random.uniform(100, 1000), 2),
                )
            )
            price = close_price
        self._health.last_data_timestamp = candles[-1].timestamp if candles else None
        logger.bind(component="connectivity").info(
            "Simulated connector generated {} candles for {} {}",
            len(candles),
            symbol,
            timeframe,
        )
        return CandleSeries(symbol.upper(), timeframe.lower(), candles)

    def _simulate_latency(self) -> float:
        started = perf_counter()
        if self.latency_ms > 0:
            sleep(self.latency_ms / 1000)
        return (perf_counter() - started) * 1000
