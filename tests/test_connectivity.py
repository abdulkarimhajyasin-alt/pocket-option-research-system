"""Tests for controlled read-only connectivity research layer."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.connectivity.csv_market_connector import CsvMarketDataConnector
from app.connectivity.data_validator import ConnectorDataValidator
from app.connectivity.errors import ConnectorUnsafeOperationError, ConnectorValidationError
from app.connectivity.models import ConnectorCapabilities
from app.connectivity.registry import ConnectorRegistry
from app.connectivity.simulated_market_connector import SimulatedMarketConnector
from app.data.models import Candle, CandleSeries
from app.runtime.connectivity_runtime import ConnectivityRuntime
from app.runtime.orchestrator import RuntimeOrchestrator


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_connector_capabilities_disable_execution_by_default() -> None:
    """Connector capabilities should be read-only by default."""
    capabilities = ConnectorCapabilities(supported_symbols=("EURUSD",), supported_timeframes=("1m",))

    assert capabilities.market_data_read
    assert not capabilities.trade_execution_enabled
    assert capabilities.supports_symbol("eurusd")


def test_connector_capabilities_reject_execution_enabled() -> None:
    """Execution-capable connectors must be rejected at model creation."""
    with pytest.raises(ValueError):
        ConnectorCapabilities(trade_execution_enabled=True)


def test_registry_registers_read_only_connectors() -> None:
    """Registry should create read-only connectors and expose capabilities."""
    registry = ConnectorRegistry()
    registry.register(
        "sim",
        lambda: SimulatedMarketConnector(
            ConnectorCapabilities(
                supported_symbols=("EURUSD",),
                supported_timeframes=("1m",),
            )
        ),
    )

    assert registry.names() == ["sim"]
    assert not registry.capabilities("sim").trade_execution_enabled


def test_read_only_connector_rejects_trade_execution() -> None:
    """Read-only connectors should expose no executable trade flow."""
    connector = SimulatedMarketConnector(
        ConnectorCapabilities(supported_symbols=("EURUSD",), supported_timeframes=("1m",))
    )

    with pytest.raises(ConnectorUnsafeOperationError):
        connector.place_trade()


def test_csv_connector_fetches_local_candles() -> None:
    """CSV connector should wrap local historical data loading."""
    connector = CsvMarketDataConnector.from_yaml(
        PROJECT_ROOT / "configs" / "connectivity" / "csv_connector.yaml"
    )
    connector.connect()

    series = connector.fetch_latest_candles("EURUSD", "1m", limit=10)

    assert len(series) == 10
    assert series.symbol == "EURUSD"
    assert connector.get_status().connected
    connector.disconnect()


def test_csv_connector_rejects_unsupported_symbol() -> None:
    """CSV connector should enforce configured symbol whitelist."""
    connector = CsvMarketDataConnector.from_yaml(
        PROJECT_ROOT / "configs" / "connectivity" / "csv_connector.yaml"
    )

    with pytest.raises(ConnectorValidationError):
        connector.fetch_historical_candles("BTCUSD", "1m", limit=1)


def test_simulated_connector_generates_ordered_m1_and_m5_candles() -> None:
    """Simulated connector should generate realistic ordered candle batches."""
    connector = SimulatedMarketConnector.from_yaml(
        PROJECT_ROOT / "configs" / "connectivity" / "simulated_connector.yaml"
    )
    connector.connect()

    m1 = connector.fetch_historical_candles("EURUSD", "1m", limit=5)
    m5 = connector.fetch_historical_candles("EURUSD", "5m", limit=5)

    assert len(m1) == 5
    assert len(m5) == 5
    assert m1.last is not None
    assert connector.get_status().last_data_timestamp == m5.last.timestamp
    connector.disconnect()


def test_data_validator_detects_missing_and_stale_data() -> None:
    """Data validator should flag gaps and stale series."""
    candles = (
        Candle("EURUSD", "1m", datetime(2020, 1, 1, tzinfo=UTC), 1.0, 1.1, 0.9, 1.0),
        Candle(
            "EURUSD",
            "1m",
            datetime(2020, 1, 1, 0, 3, tzinfo=UTC),
            1.0,
            1.1,
            0.9,
            1.0,
        ),
    )
    series = CandleSeries("EURUSD", "1m", candles)

    result = ConnectorDataValidator().validate(series, stale_after_minutes=1)

    assert result.passed
    assert any("Missing candle" in warning for warning in result.warnings)
    assert any("Stale data" in warning for warning in result.warnings)


def test_data_validator_rejects_empty_series() -> None:
    """Empty connector output should be a critical validation failure."""
    result = ConnectorDataValidator().validate(CandleSeries("EURUSD", "1m", ()))

    assert not result.passed
    assert result.errors == ["Candle series is empty"]


def test_connectivity_runtime_fetches_and_validates() -> None:
    """Connectivity runtime should coordinate connector heartbeat and validation."""
    connector = SimulatedMarketConnector(
        ConnectorCapabilities(
            supported_symbols=("EURUSD",),
            supported_timeframes=("1m",),
        )
    )
    runtime = ConnectivityRuntime(connector)
    runtime.initialize()

    series, validation = runtime.fetch_and_validate("EURUSD", "1m", limit=5)

    assert len(series) == 5
    assert validation.passed
    assert runtime.diagnostics().connected
    runtime.shutdown()


def test_data_validator_warns_on_stale_recent_threshold() -> None:
    """Stale data detection should honor configurable freshness thresholds."""
    timestamp = datetime.now(tz=UTC) - timedelta(minutes=10)
    series = CandleSeries(
        "EURUSD",
        "1m",
        (Candle("EURUSD", "1m", timestamp, 1.0, 1.1, 0.9, 1.0),),
    )

    result = ConnectorDataValidator().validate(series, stale_after_minutes=1)

    assert any("Stale data" in warning for warning in result.warnings)


def test_orchestrator_diagnostics_include_connectivity() -> None:
    """Orchestrator diagnostics should include connectivity config and service graph."""
    orchestrator = RuntimeOrchestrator(PROJECT_ROOT, environment="local")

    diagnostics = orchestrator.bootstrap()

    assert diagnostics.connectivity["read_only"]
    assert "connectivity_runtime" in diagnostics.dependency_graph
    orchestrator.shutdown()
