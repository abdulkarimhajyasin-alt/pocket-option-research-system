from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.live_observation.replay import ObservationReplayEngine
from app.live_observation.scheduler import SUPPORTED_SPEEDS
from app.live_observation.service import LiveObservationService
from app.live_observation.timeline import ObservationTimelineEngine
from app.live_observation.timeline import ObservationTimelineSource
from app.live_observation.validation import ReplayValidationEngine


def test_live_observation_replay_engines_are_bounded() -> None:
    observations = ObservationTimelineSource(Path(".")).load()
    replay = ObservationReplayEngine().replay(observations, speed_multiplier=10)
    timeline = ObservationTimelineEngine().build(observations)
    validation = ReplayValidationEngine().validate(replay, timeline)

    assert len(observations) >= 5
    assert replay.speed_multiplier in SUPPORTED_SPEEDS
    assert replay.pause_supported is True
    assert replay.resume_supported is True
    assert replay.reset_supported is True
    assert 0 <= replay.score <= 100
    assert 0 <= timeline.score <= 100
    assert 0 <= validation.score <= 100


def test_live_observation_service_generates_outputs() -> None:
    run = LiveObservationService(Path(".")).run()

    assert run.result.metadata["live_observation_replay"] is True
    assert run.result.metadata["observation_only"] is True
    assert run.result.metadata["not_execution"] is True
    assert run.result.metadata["not_order_placement"] is True
    assert run.result.metadata["not_account_login"] is True
    assert run.result.metadata["not_broker_authentication"] is True
    assert run.result.metadata["not_credential_handling"] is True
    assert run.result.metadata["not_browser_automation"] is True
    assert run.result.metadata["not_broker_control"] is True
    assert run.result.to_dict()["live_observation_replay"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_live_observation_dashboard_and_api_are_arabic() -> None:
    LiveObservationService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/live-observation")
    api = client.get("/api/live-observation")

    assert page.status_code == 200
    assert api.status_code == 200
    assert "محرك إعادة تشغيل المراقبة" in page.text
    assert "التسلسل الزمني" in page.text
    assert "استقرار التشغيل" in page.text
    assert "Live Observation" not in page.text
    assert api.json()["summary"]["live_observation_replay"] is True
