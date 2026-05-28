"""Read-only market-data connector contracts."""

from abc import ABC, abstractmethod

from loguru import logger

from app.connectivity.errors import ConnectorUnsafeOperationError, ConnectorValidationError
from app.connectivity.health import ConnectorHealthSnapshot
from app.connectivity.models import ConnectorCapabilities
from app.data.models import CandleSeries


class BaseReadOnlyConnector(ABC):
    """Base class for safe read-only market-data connectors."""

    name: str = "base_read_only_connector"

    def __init__(self, capabilities: ConnectorCapabilities) -> None:
        if capabilities.trade_execution_enabled:
            raise ConnectorValidationError("Read-only connectors cannot enable execution")
        self._capabilities = capabilities
        self._health = ConnectorHealthSnapshot()

    @abstractmethod
    def connect(self) -> None:
        """Open the connector lifecycle."""

    @abstractmethod
    def disconnect(self) -> None:
        """Close the connector lifecycle."""

    @abstractmethod
    def ping(self) -> ConnectorHealthSnapshot:
        """Run a connector heartbeat."""

    def get_status(self) -> ConnectorHealthSnapshot:
        """Return current connector health."""
        return self._health

    def get_capabilities(self) -> ConnectorCapabilities:
        """Return read-only connector capabilities."""
        return self._capabilities

    def validate_environment(self) -> None:
        """Validate connector safety constraints."""
        if self._capabilities.trade_execution_enabled:
            logger.bind(component="connectivity").error("Unsafe execution capability requested")
            raise ConnectorValidationError("Execution capability is forbidden for connectors")
        logger.bind(component="connectivity").info("Connector environment validated: {}", self.name)

    @abstractmethod
    def fetch_latest_candles(self, symbol: str, timeframe: str, limit: int) -> CandleSeries:
        """Fetch latest read-only candles."""

    @abstractmethod
    def fetch_historical_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int | None = None,
    ) -> CandleSeries:
        """Fetch historical read-only candles."""

    def assert_market_supported(self, symbol: str, timeframe: str) -> None:
        """Validate that symbol and timeframe are supported."""
        if not self._capabilities.supports_symbol(symbol):
            raise ConnectorValidationError(f"Unsupported connector symbol: {symbol}")
        if not self._capabilities.supports_timeframe(timeframe):
            raise ConnectorValidationError(f"Unsupported connector timeframe: {timeframe}")

    def place_trade(self, *_args: object, **_kwargs: object) -> None:
        """Always reject execution attempts on read-only connectors."""
        logger.bind(component="connectivity").error(
            "Unsafe operation attempted on read-only connector {}",
            self.name,
        )
        raise ConnectorUnsafeOperationError("Connectors are read-only and cannot place trades")
