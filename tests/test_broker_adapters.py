"""Tests for broker adapter architecture."""

from pathlib import Path
from time import perf_counter

import pytest

from app.brokers.capabilities import BrokerCapabilities
from app.brokers.demo_adapter import DemoBrokerAdapter
from app.brokers.errors import BrokerValidationError
from app.brokers.health import BrokerHealthStatus
from app.brokers.models import BrokerMode
from app.brokers.registry import BrokerRegistry
from app.runtime.broker_runtime import BrokerRuntime


def test_broker_registry_registers_and_creates_demo_adapter() -> None:
    registry = BrokerRegistry()
    registry.register("demo", DemoBrokerAdapter)

    broker = registry.create("demo")

    assert "demo" in registry.names()
    assert broker.get_capabilities().demo_supported is True


def test_demo_adapter_lifecycle_and_health_snapshot() -> None:
    broker = DemoBrokerAdapter()

    broker.connect()
    assert broker.ping() is True
    health = broker.health_snapshot()
    broker.disconnect()

    assert health.status == BrokerHealthStatus.CONNECTED
    assert health.connected is True
    assert broker.get_status().connected is False


def test_demo_adapter_rejects_live_mode() -> None:
    broker = DemoBrokerAdapter(mode=BrokerMode.LIVE)

    with pytest.raises(BrokerValidationError):
        broker.validate_environment()


def test_demo_adapter_rejects_live_capability() -> None:
    broker = DemoBrokerAdapter(
        capabilities=BrokerCapabilities(
            demo_supported=True,
            live_supported=True,
            supported_symbols=("EURUSD",),
            supported_timeframes=("1m",),
        )
    )

    with pytest.raises(BrokerValidationError):
        broker.connect()


def test_demo_adapter_simulates_latency() -> None:
    broker = DemoBrokerAdapter(latency_ms=5)
    broker.connect()
    start = perf_counter()

    broker.ping()

    assert (perf_counter() - start) >= 0.005


def test_broker_runtime_reconnect_cycle() -> None:
    broker = DemoBrokerAdapter(max_reconnect_attempts=1)
    runtime = BrokerRuntime(broker)
    runtime.initialize()

    assert broker.reconnect() is True
    assert broker.reconnect() is False
    diagnostics = runtime.diagnostics()
    runtime.shutdown()

    assert diagnostics.connected is True
    assert diagnostics.health["reconnect_attempts"] == 1


def test_demo_adapter_loads_capabilities_from_yaml() -> None:
    path = Path("configs/brokers/demo_broker.yaml")
    broker = DemoBrokerAdapter.from_yaml(path)

    assert broker.supports_symbol("EURUSD") is True
    assert broker.supports_timeframe("1m") is True
    assert broker.get_capabilities().live_supported is False
