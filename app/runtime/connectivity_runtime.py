"""Runtime coordinator for read-only market-data connectors."""

from dataclasses import dataclass

from loguru import logger

from app.connectivity.base_connector import BaseReadOnlyConnector
from app.connectivity.data_validator import ConnectorDataValidator, DataValidationResult
from app.connectivity.errors import ConnectorValidationError
from app.connectivity.health import ConnectorHealthSnapshot
from app.data.models import CandleSeries


@dataclass(frozen=True)
class ConnectivityDiagnostics:
    """Connector runtime diagnostic snapshot."""

    connected: bool
    health: dict[str, object]
    capabilities: dict[str, object]


class ConnectivityRuntime:
    """Initializes, validates, and monitors read-only connector services."""

    def __init__(
        self,
        connector: BaseReadOnlyConnector,
        validator: ConnectorDataValidator | None = None,
        stale_after_minutes: int = 1440,
    ) -> None:
        self.connector = connector
        self.validator = validator or ConnectorDataValidator()
        self.stale_after_minutes = stale_after_minutes

    def initialize(self) -> None:
        """Validate and connect a read-only connector."""
        logger.bind(component="connectivity").info("Initializing connectivity runtime")
        self.connector.validate_environment()
        capabilities = self.connector.get_capabilities()
        if capabilities.trade_execution_enabled:
            raise ConnectorValidationError(
                "Connectivity runtime rejects execution-capable connectors"
            )
        self.connector.connect()

    def heartbeat(self) -> ConnectorHealthSnapshot:
        """Run a connector heartbeat."""
        health = self.connector.ping()
        logger.bind(component="connectivity").info("Connector heartbeat: {}", health.to_dict())
        return health

    def fetch_and_validate(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
        latest: bool = False,
    ) -> tuple[CandleSeries, DataValidationResult]:
        """Fetch connector candles and validate ingestion quality."""
        if latest:
            series = self.connector.fetch_latest_candles(symbol, timeframe, limit)
        else:
            series = self.connector.fetch_historical_candles(symbol, timeframe, limit)
        validation = self.validator.validate(
            series,
            stale_after_minutes=self.stale_after_minutes,
        )
        return series, validation

    def diagnostics(self) -> ConnectivityDiagnostics:
        """Return connectivity runtime diagnostics."""
        health = self.connector.get_status()
        return ConnectivityDiagnostics(
            connected=health.connected,
            health=health.to_dict(),
            capabilities=self.connector.get_capabilities().to_dict(),
        )

    def shutdown(self) -> None:
        """Safely disconnect the connector."""
        logger.bind(component="connectivity").info("Connectivity runtime shutdown")
        self.connector.disconnect()
