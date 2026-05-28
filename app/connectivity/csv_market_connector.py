"""Local CSV market-data connector for read-only ingestion validation."""

from pathlib import Path
from time import perf_counter
from typing import Any

import yaml
from loguru import logger

from app.connectivity.base_connector import BaseReadOnlyConnector
from app.connectivity.models import ConnectorCapabilities
from app.data.csv_loader import CsvCandleLoader
from app.data.models import CandleSeries


class CsvMarketDataConnector(BaseReadOnlyConnector):
    """Read-only connector that wraps local CSV historical market data."""

    name = "csv_market_connector"

    def __init__(
        self,
        data_path: Path | str,
        capabilities: ConnectorCapabilities,
        loader: CsvCandleLoader | None = None,
    ) -> None:
        super().__init__(capabilities)
        self.data_path = Path(data_path)
        self.loader = loader or CsvCandleLoader()

    @classmethod
    def from_yaml(cls, path: Path | str) -> "CsvMarketDataConnector":
        """Create a CSV connector from YAML config."""
        config_path = Path(path)
        raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        capabilities = ConnectorCapabilities(
            market_data_read=bool(raw.get("market_data_read", True)),
            historical_data_read=bool(raw.get("historical_data_read", True)),
            account_info_read=bool(raw.get("account_info_read", False)),
            trade_execution_enabled=bool(raw.get("trade_execution_enabled", False)),
            supported_symbols=tuple(raw.get("symbols", [])),
            supported_timeframes=tuple(raw.get("timeframes", [])),
            supported_data_modes=tuple(raw.get("data_modes", ["historical", "latest"])),
        )
        return cls(data_path=raw["data_path"], capabilities=capabilities)

    def connect(self) -> None:
        """Validate local file availability."""
        self.validate_environment()
        if not self.data_path.exists():
            raise FileNotFoundError(f"CSV connector data file not found: {self.data_path}")
        self._health.mark_connected()
        logger.bind(component="connectivity").info(
            "CSV connector connected path={}",
            self.data_path,
        )

    def disconnect(self) -> None:
        """Disconnect the local connector lifecycle."""
        self._health.mark_disconnected()
        logger.bind(component="connectivity").info("CSV connector disconnected")

    def ping(self) -> Any:
        """Run a local file heartbeat."""
        started = perf_counter()
        exists = self.data_path.exists()
        if not exists:
            self._health.mark_error()
        else:
            self._health.mark_connected((perf_counter() - started) * 1000)
        logger.bind(component="connectivity").info("CSV connector heartbeat exists={}", exists)
        return self._health

    def fetch_latest_candles(self, symbol: str, timeframe: str, limit: int) -> CandleSeries:
        """Fetch latest candles from the local CSV dataset."""
        series = self.fetch_historical_candles(symbol, timeframe)
        selected = tuple(series)[-limit:] if limit > 0 else tuple()
        return CandleSeries(series.symbol, series.timeframe, selected)

    def fetch_historical_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int | None = None,
    ) -> CandleSeries:
        """Fetch historical candles from the local CSV dataset."""
        self.assert_market_supported(symbol, timeframe)
        logger.bind(component="connectivity").info(
            "CSV connector fetching historical candles symbol={} timeframe={}",
            symbol,
            timeframe,
        )
        series = self.loader.load(self.data_path, symbol=symbol, timeframe=timeframe)
        candles = tuple(series)
        if limit is not None:
            candles = candles[-limit:]
        if candles:
            self._health.last_data_timestamp = candles[-1].timestamp
        return CandleSeries(series.symbol, series.timeframe, candles)
