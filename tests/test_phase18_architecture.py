"""Tests for Phase 18 architecture hardening layers."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from time import sleep

import pytest

from app.brokers.paper_broker import PaperBroker
from app.dashboard.actions import DashboardActionRunner
from app.dashboard.models import ActionDefinition
from app.events import DatasetEvent, RuntimeEvent, StrategyEvent, ValidationEvent
from app.i18n.validators import ArabicDashboardValidator
from app.jobs.manager import JobManager
from app.jobs.models import JobResult, JobStatus
from app.jobs.registry import JobRegistry
from app.reports.repository import ReportIndex, ReportRepository
from app.risk.risk_engine import RiskConfig, RiskEngine
from app.runtime.factory import RuntimeDependencyFactory
from app.runtime.pipeline import CandleProcessingPipeline
from app.runtime.runtime_manager import RuntimeConfig
from app.runtime.runtime_state import RuntimeMode, RuntimeState
from app.runtime.health import HealthMonitor
from app.runtime.kill_switch import KillSwitch
from app.execution.execution_manager import ExecutionManager
from app.data.models import Candle, CandleSeries
from app.strategies.sample_strategy import SampleCandleDirectionStrategy


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _candle(index: int, open_price: float, close: float) -> Candle:
    return Candle(
        symbol="EURUSD",
        timeframe="1m",
        timestamp=datetime(2026, 1, 1, 12, index, tzinfo=UTC),
        open=open_price,
        high=max(open_price, close) + 0.0002,
        low=min(open_price, close) - 0.0002,
        close=close,
    )


def test_report_repository_indexes_caches_and_rejects_traversal(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "unit.json").write_text(json.dumps({"score": 1}), encoding="utf-8")

    repository = ReportRepository(tmp_path)
    listed = repository.list_reports()
    second = repository.list_reports()
    content = repository.get_report(listed[0].report_id)

    assert listed == second
    assert content is not None and content.json_data == {"score": 1}
    assert repository.metrics.refresh_count == 1
    assert repository.metrics.cache_hits >= 1
    with pytest.raises(ValueError):
        ReportIndex(tmp_path).validate_report_path(tmp_path / "outside.json")


def test_runtime_dependency_factory_creates_safe_dependencies() -> None:
    config = RuntimeConfig(
        max_candles=1,
        persistence_enabled=False,
        risk_profile=str(PROJECT_ROOT / "configs/risk/base_risk.yaml"),
    )
    factory = RuntimeDependencyFactory(PROJECT_ROOT)
    broker = factory.create_broker(config)
    persistence = factory.create_persistence(config)

    assert broker.get_capabilities().live_supported is False
    assert persistence.enabled is False
    assert factory.create_runtime_state(config).mode == RuntimeMode.PAPER


def test_candle_processing_pipeline_processes_one_candle() -> None:
    candles = CandleSeries("EURUSD", "1m", [_candle(0, 1.1, 1.2)])
    broker = PaperBroker()
    broker.connect()
    manager = ExecutionManager(RiskEngine(config=RiskConfig(max_trades_per_day=10)), broker)
    state = RuntimeState(mode=RuntimeMode.PAPER)
    state.start()
    pipeline = CandleProcessingPipeline(
        SampleCandleDirectionStrategy(),
        manager,
        state,
        HealthMonitor(),
        KillSwitch(),
    )

    result = pipeline.process(candles[0], candles, 0)

    assert not result.errors
    assert state.metrics.processed_candles == 1
    assert state.metrics.generated_signals == 1


def test_domain_events_are_typed_and_serializable() -> None:
    events = [
        StrategyEvent(event_type="strategy.signal", aggregate_id="s"),
        ValidationEvent(event_type="validation.run", aggregate_id="v"),
        DatasetEvent(event_type="dataset.quality", aggregate_id="d"),
        RuntimeEvent(event_type="runtime.state", aggregate_id="r"),
    ]

    assert {event.domain for event in events} == {"strategy", "validation", "dataset", "runtime"}
    assert all(event.to_dict()["event_id"] for event in events)


def test_dashboard_jobs_are_queued_and_observable() -> None:
    registry = JobRegistry()
    registry.register(
        ActionDefinition("unit", "مهمة اختبار", "تشغيل اختبار", ("unit.py",)),
        lambda: JobResult(exit_code=0, stdout="ok"),
    )
    manager = JobManager(registry, max_workers=1)
    try:
        record = manager.enqueue("unit")
        for _ in range(20):
            latest = manager.get(record.run_id)
            if latest and latest.status == JobStatus.COMPLETED:
                break
            sleep(0.01)
        latest = manager.get(record.run_id)
        assert latest is not None
        assert latest.status == JobStatus.COMPLETED
        assert latest.result is not None and latest.result.stdout == "ok"
    finally:
        manager.shutdown()


def test_arabic_dashboard_validation_passes() -> None:
    result = ArabicDashboardValidator(PROJECT_ROOT).validate()
    assert result.passed, result.to_dict()


def test_dashboard_action_runner_exposes_job_registry(tmp_path: Path) -> None:
    registry = DashboardActionRunner(tmp_path).job_registry()
    assert "validation" in registry.names()
