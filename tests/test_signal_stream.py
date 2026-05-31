from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.signal_stream.models import SignalDirection
from app.signal_stream.queue import SignalQueueEngine
from app.signal_stream.service import SignalStreamService
from app.signal_stream.stream import SignalStreamEngine
from app.signal_stream.timeline import SignalTimelineEngine
from app.signal_stream.validation import SignalStreamValidationEngine


def test_signal_stream_engines_are_bounded() -> None:
    stream = SignalStreamEngine(Path(".")).run()
    queue = SignalQueueEngine().manage(stream.events)
    timeline = SignalTimelineEngine().build(stream.events)
    validation = SignalStreamValidationEngine().validate(stream.events, timeline)

    assert len(stream.events) >= 5
    assert {item.direction for item in stream.events}.issubset(set(SignalDirection))
    assert 0 <= stream.score <= 100
    assert 0 <= queue.score <= 100
    assert 0 <= timeline.score <= 100
    assert 0 <= validation.score <= 100


def test_signal_stream_service_generates_outputs() -> None:
    run = SignalStreamService(Path(".")).run()

    assert run.result.metadata["research_only"] is True
    assert run.result.metadata["signal_generation_only"] is True
    assert run.result.metadata["not_execution"] is True
    assert run.result.metadata["not_order_placement"] is True
    assert run.result.metadata["not_account_login"] is True
    assert run.result.metadata["not_broker_authentication"] is True
    assert run.result.metadata["not_credential_handling"] is True
    assert run.result.metadata["not_browser_automation"] is True
    assert run.result.metadata["not_broker_control"] is True
    assert run.result.to_dict()["signal_generation_only"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_signal_stream_dashboard_and_api_are_arabic() -> None:
    SignalStreamService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/signal-stream")
    api = client.get("/api/signal-stream")

    assert page.status_code == 200
    assert api.status_code == 200
    assert "محرك تدفق الإشارات" in page.text
    assert "توزيع الإشارات" in page.text
    assert "كثافة الإشارات" in page.text
    assert "Signal Stream" not in page.text
    assert api.json()["summary"]["signal_generation_only"] is True
