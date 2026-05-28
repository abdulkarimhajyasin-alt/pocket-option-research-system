"""Tests for configuration and orchestration infrastructure."""

from pathlib import Path

import pytest

from app.config.config_manager import ConfigManager
from app.config.resolver import ConfigResolver, deep_merge
from app.runtime.composition import RuntimeComposer
from app.runtime.container import ServiceContainer
from app.runtime.modes import ModePolicy, OperationalMode
from app.runtime.orchestrator import RuntimeOrchestrator
from app.runtime.startup_checks import StartupValidator


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_config_manager_loads_environment_with_inheritance() -> None:
    """Research environment should inherit local defaults and override mode."""
    config = ConfigManager(PROJECT_ROOT).load("research")

    assert config.environment.name.value == "research"
    assert config.environment.runtime_config == "configs/runtime/safe_runtime.yaml"
    assert config.get("strategy.name") == "sample_candle_direction_strategy"
    assert config.validation.passed


def test_config_resolver_applies_nested_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment variables should override nested resolved settings."""
    monkeypatch.setenv("TRADING_RUNTIME__MAX_CANDLES", "7")

    resolved = ConfigResolver().resolve([{"runtime": {"max_candles": 120}}])

    assert resolved["runtime"]["max_candles"] == 7


def test_deep_merge_preserves_nested_defaults() -> None:
    """Nested config merges should retain unspecified defaults."""
    merged = deep_merge({"runtime": {"mode": "paper", "stake": 1}}, {"runtime": {"stake": 2}})

    assert merged == {"runtime": {"mode": "paper", "stake": 2}}


def test_service_container_lazily_initializes_singletons() -> None:
    """Container should initialize singleton services once."""
    calls = {"count": 0}
    container = ServiceContainer()

    def factory() -> object:
        calls["count"] += 1
        return object()

    container.register("example", factory)
    first = container.get("example")
    second = container.get("example")

    assert first is second
    assert calls["count"] == 1
    assert container.dependency_graph()["example"]["initialized"]


def test_startup_validator_accepts_demo_only_environment() -> None:
    """Startup checks should pass for the local demo-safe environment."""
    config = ConfigManager(PROJECT_ROOT).load("local")
    result = StartupValidator(PROJECT_ROOT).validate(config)

    assert result.passed
    assert not result.failures


def test_mode_policy_rejects_unknown_mode() -> None:
    """Operational mode policy should reject unsupported modes."""
    assert ModePolicy().validate(OperationalMode.PAPER).allowed
    assert not ModePolicy().validate("live").allowed


def test_runtime_composition_registers_core_services() -> None:
    """Runtime composer should expose the core dependency graph."""
    config = ConfigManager(PROJECT_ROOT).load("local")
    composition = RuntimeComposer(PROJECT_ROOT).compose(config)

    assert "runtime_manager" in composition.container.names()
    assert "risk_engine" in composition.container.names()
    composition.runtime_manager.persistence.close()


def test_orchestrator_bootstrap_exports_diagnostics() -> None:
    """Orchestrator bootstrap should validate and compose without starting runtime."""
    orchestrator = RuntimeOrchestrator(PROJECT_ROOT, environment="local")

    diagnostics = orchestrator.bootstrap()

    assert diagnostics.environment == "local"
    assert diagnostics.startup["passed"]
    assert "runtime_manager" in diagnostics.dependency_graph
    orchestrator.shutdown()
