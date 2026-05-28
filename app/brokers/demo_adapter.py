"""Demo broker adapter that wraps the local paper broker."""

from pathlib import Path
from time import perf_counter, sleep
from typing import Any

import yaml
from loguru import logger

from app.brokers.base_broker import BaseBroker
from app.brokers.capabilities import BrokerCapabilities
from app.brokers.errors import BrokerConnectionError, BrokerValidationError
from app.brokers.health import BrokerHealthSnapshot, BrokerHealthStatus, utc_now
from app.brokers.models import BrokerMode, BrokerStatus
from app.brokers.paper_broker import PaperBroker
from app.data.models import Candle
from app.execution.positions import Position
from app.signals.signal import TradeSignal


class DemoBrokerAdapter(BaseBroker):
    """Demo-only adapter that simulates a real broker lifecycle locally."""

    name = "demo_broker"

    def __init__(
        self,
        paper_broker: PaperBroker | None = None,
        capabilities: BrokerCapabilities | None = None,
        mode: BrokerMode = BrokerMode.DEMO,
        latency_ms: float = 0.0,
        max_reconnect_attempts: int = 3,
    ) -> None:
        self.mode = mode
        self.paper_broker = paper_broker or PaperBroker()
        self._capabilities = capabilities or BrokerCapabilities(
            demo_supported=True,
            live_supported=False,
            supported_symbols=("EURUSD", "GBPUSD", "USDJPY"),
            supported_timeframes=("1m", "5m", "15m"),
            payout_supported=True,
            trade_types=("binary_option",),
            historical_data_supported=False,
        )
        self.latency_ms = latency_ms
        self.max_reconnect_attempts = max_reconnect_attempts
        self._connected = False
        self._last_heartbeat = None
        self._last_latency_ms = 0.0
        self._error_count = 0
        self._reconnect_attempts = 0

    @classmethod
    def from_yaml(cls, path: Path | str) -> "DemoBrokerAdapter":
        """Create a demo adapter from YAML configuration."""
        config_path = Path(path)
        raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        capabilities_raw = raw.get("capabilities", {})
        broker_raw = raw.get("paper_broker", {})
        capabilities = BrokerCapabilities(
            demo_supported=bool(capabilities_raw.get("demo_supported", True)),
            live_supported=bool(capabilities_raw.get("live_supported", False)),
            supported_symbols=tuple(capabilities_raw.get("supported_symbols", ["EURUSD"])),
            supported_timeframes=tuple(capabilities_raw.get("supported_timeframes", ["1m"])),
            payout_supported=bool(capabilities_raw.get("payout_supported", True)),
            trade_types=tuple(capabilities_raw.get("trade_types", ["binary_option"])),
            historical_data_supported=bool(
                capabilities_raw.get("historical_data_supported", False)
            ),
        )
        adapter = cls(
            paper_broker=PaperBroker(
                initial_balance=float(broker_raw.get("initial_balance", 10_000.0)),
                payout_percentage=float(broker_raw.get("payout_percentage", 0.80)),
                stake=float(broker_raw.get("stake", 1.0)),
                expiry_candles=int(broker_raw.get("expiry_candles", 1)),
            ),
            capabilities=capabilities,
            mode=BrokerMode(raw.get("mode", BrokerMode.DEMO.value)),
            latency_ms=float(raw.get("latency_ms", 0.0)),
            max_reconnect_attempts=int(raw.get("max_reconnect_attempts", 3)),
        )
        logger.bind(component="broker").info(
            "Demo broker config loaded path={} capabilities={}",
            config_path,
            capabilities.to_dict(),
        )
        return adapter

    def connect(self) -> None:
        """Connect the demo adapter after enforcing demo-only safety."""
        logger.bind(component="broker").info("Demo broker connection attempt")
        self.validate_environment()
        self._simulate_latency()
        try:
            self.paper_broker.connect()
            self._connected = True
            self._last_heartbeat = utc_now()
            logger.bind(component="broker").info("Demo broker connected")
        except Exception as exc:
            self._error_count += 1
            raise BrokerConnectionError(str(exc)) from exc

    def disconnect(self) -> None:
        """Disconnect the demo adapter safely."""
        self._simulate_latency()
        self.paper_broker.disconnect()
        self._connected = False
        logger.bind(component="broker").info("Demo broker disconnected")

    def ping(self) -> bool:
        """Run a simulated heartbeat."""
        if not self._connected:
            self._error_count += 1
            logger.bind(component="broker").warning("Demo broker heartbeat failed")
            return False
        start = perf_counter()
        self._simulate_latency()
        self._last_latency_ms = (perf_counter() - start) * 1000
        self._last_heartbeat = utc_now()
        logger.bind(component="broker").info(
            "Demo broker heartbeat latency_ms={}",
            round(self._last_latency_ms, 4),
        )
        return True

    def reconnect(self) -> bool:
        """Attempt a bounded reconnect cycle."""
        if self._reconnect_attempts >= self.max_reconnect_attempts:
            self._error_count += 1
            return False
        self._reconnect_attempts += 1
        logger.bind(component="broker").info(
            "Demo broker reconnect attempt {}",
            self._reconnect_attempts,
        )
        self.disconnect()
        self.connect()
        return True

    def get_balance(self) -> float:
        """Return simulated balance."""
        return self.paper_broker.get_balance()

    def place_trade(self, signal: TradeSignal, candle: Candle | None = None) -> dict[str, Any]:
        """Place a local paper trade through the adapter boundary."""
        self._simulate_latency()
        if not self.supports_symbol(signal.symbol):
            raise BrokerValidationError(f"Unsupported symbol: {signal.symbol}")
        if not self.supports_timeframe(signal.timeframe):
            raise BrokerValidationError(f"Unsupported timeframe: {signal.timeframe}")
        return self.paper_broker.place_trade(signal, candle)

    def settle_trade(self, trade_id: str, candle: Candle) -> dict[str, Any]:
        """Settle a local paper trade."""
        self._simulate_latency()
        return self.paper_broker.settle_trade(trade_id, candle)

    def get_open_positions(self) -> list[Position]:
        """Return open local positions."""
        return self.paper_broker.get_open_positions()

    def get_trade_history(self) -> list[dict[str, Any]]:
        """Return local paper lifecycle history."""
        return self.paper_broker.get_trade_history()

    def get_status(self) -> BrokerStatus:
        """Return broker status."""
        return BrokerStatus(
            name=self.name,
            mode=self.mode,
            connected=self._connected,
            health=self.health_snapshot(),
        )

    def get_capabilities(self) -> BrokerCapabilities:
        """Return adapter capabilities."""
        logger.bind(component="broker").info("Demo broker capabilities requested")
        return self._capabilities

    def health_snapshot(self) -> BrokerHealthSnapshot:
        """Return current broker health."""
        if self._connected and self._error_count == 0:
            status = BrokerHealthStatus.CONNECTED
        elif self._connected:
            status = BrokerHealthStatus.DEGRADED
        else:
            status = BrokerHealthStatus.DISCONNECTED
        return BrokerHealthSnapshot(
            status=status,
            connected=self._connected,
            last_heartbeat=self._last_heartbeat,
            response_latency_ms=self._last_latency_ms,
            error_count=self._error_count,
            reconnect_attempts=self._reconnect_attempts,
        )

    def validate_environment(self) -> bool:
        """Refuse live or unsafe adapter modes."""
        if self.mode == BrokerMode.LIVE:
            raise BrokerValidationError("Live broker mode is disabled in this platform phase")
        if self._capabilities.live_supported:
            raise BrokerValidationError("Live broker capabilities are not allowed")
        if not self._capabilities.demo_supported:
            raise BrokerValidationError("Demo broker support is required")
        logger.bind(component="broker").info("Demo broker environment validated")
        return True

    def _simulate_latency(self) -> None:
        if self.latency_ms <= 0:
            return
        logger.bind(component="broker").info("Simulating broker latency {}ms", self.latency_ms)
        sleep(self.latency_ms / 1000)
