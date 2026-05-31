"""Live observation replay service orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.live_observation.analytics import LiveObservationAnalytics
from app.live_observation.analytics import ReplayQualityEngine
from app.live_observation.analytics import ReplayReadinessEngine
from app.live_observation.diagnostics import ReplayDiagnosticsEngine
from app.live_observation.diagnostics import ReplayRecommendationEngine
from app.live_observation.models import LiveObservationResult
from app.live_observation.replay import ObservationReplayEngine
from app.live_observation.reports import LiveObservationReportWriter
from app.live_observation.state import ReplayStateEngine
from app.live_observation.storage import LiveObservationStorage
from app.live_observation.timeline import ObservationTimelineEngine
from app.live_observation.timeline import ObservationTimelineSource
from app.live_observation.validation import ReplayValidationEngine


@dataclass(frozen=True)
class LiveObservationRunResult:
    """Result of one live observation replay run."""

    result: LiveObservationResult
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class LiveObservationService:
    """Replay local passive observations as deterministic simulated live flow."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.source = ObservationTimelineSource(self.project_root)
        self.replay = ObservationReplayEngine()
        self.timeline = ObservationTimelineEngine()
        self.state = ReplayStateEngine()
        self.validation = ReplayValidationEngine()
        self.quality = ReplayQualityEngine()
        self.readiness = ReplayReadinessEngine()
        self.diagnostics = ReplayDiagnosticsEngine()
        self.recommendations = ReplayRecommendationEngine()
        self.analytics = LiveObservationAnalytics()
        self.storage = LiveObservationStorage(
            self.project_root / "storage" / "live_observation"
        )
        self.reports = LiveObservationReportWriter(
            self.project_root / "reports" / "live_observation"
        )

    def run(self, speed_multiplier: int = 10) -> LiveObservationRunResult:
        observations = self.source.load()
        replay = self.replay.replay(observations, speed_multiplier=speed_multiplier)
        timeline = self.timeline.build(observations)
        validation = self.validation.validate(replay, timeline)
        quality = self.quality.evaluate(replay, timeline, validation)
        readiness = self.readiness.evaluate(replay, timeline, quality)
        state = self.state.evaluate(replay)
        diagnostics = self.diagnostics.evaluate(
            observations,
            timeline,
            quality,
            readiness,
            validation,
        )
        recommendations = self.recommendations.generate(diagnostics)
        result = LiveObservationResult(
            timestamp=datetime.now(UTC),
            observations=observations,
            replay=replay,
            timeline=timeline,
            state=state,
            quality=quality,
            readiness=readiness,
            validation=validation,
            diagnostics=diagnostics,
            recommendations=recommendations,
            metadata={
                "research_only": True,
                "observation_only": True,
                "live_observation_replay": True,
                "not_execution": True,
                "not_order_placement": True,
                "not_account_login": True,
                "not_broker_authentication": True,
                "not_credential_handling": True,
                "not_browser_automation": True,
                "not_broker_control": True,
            },
        )
        analytics = self.analytics.summarize(result)
        storage_paths = self.storage.save(result, analytics)
        report_paths = self.reports.export(analytics)
        return LiveObservationRunResult(result, analytics, storage_paths, report_paths)
