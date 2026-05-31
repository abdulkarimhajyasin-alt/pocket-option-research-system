"""Analytics engines for live observation replay."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.live_observation.models import LiveObservationResult
from app.live_observation.models import ReplayQualityResult
from app.live_observation.models import ReplayReadinessResult
from app.live_observation.models import ReplayResult
from app.live_observation.models import ReplayValidationResult
from app.live_observation.models import TimelineResult
from app.live_observation.scoring import average


class ReplayQualityEngine:
    """Evaluate replay consistency, completeness, reliability, and stability."""

    def evaluate(
        self,
        replay: ReplayResult,
        timeline: TimelineResult,
        validation: ReplayValidationResult,
    ) -> ReplayQualityResult:
        consistency = validation.replay_consistency
        completeness = validation.observation_completeness
        reliability = average([replay.score, timeline.score, validation.score])
        stability = average([timeline.coverage, validation.sequence_integrity, replay.score])
        return ReplayQualityResult(
            score=average([consistency, completeness, reliability, stability]),
            consistency=consistency,
            completeness=completeness,
            reliability=reliability,
            stability=stability,
        )


class ReplayReadinessEngine:
    """Evaluate replay, timeline, observation, and infrastructure readiness."""

    def evaluate(
        self,
        replay: ReplayResult,
        timeline: TimelineResult,
        quality: ReplayQualityResult,
    ) -> ReplayReadinessResult:
        replay_readiness = replay.score
        timeline_readiness = timeline.score
        observation_readiness = quality.completeness
        infrastructure_readiness = (
            100.0
            if replay.pause_supported
            and replay.resume_supported
            and replay.reset_supported
            else 50.0
        )
        return ReplayReadinessResult(
            score=average(
                [
                    replay_readiness,
                    timeline_readiness,
                    observation_readiness,
                    infrastructure_readiness,
                ]
            ),
            replay_readiness=replay_readiness,
            timeline_readiness=timeline_readiness,
            observation_readiness=observation_readiness,
            infrastructure_readiness=infrastructure_readiness,
        )


class LiveObservationAnalytics:
    """Generate replay dashboard and report analytics."""

    def summarize(self, result: LiveObservationResult) -> dict[str, Any]:
        diagnostics = Counter(item.severity for item in result.diagnostics)
        recommendations = Counter(item.title for item in result.recommendations)
        source_distribution = Counter(item.source for item in result.observations)
        timeline_activity = {
            str(row.get("sequence")): float(row.get("quality", 0.0))
            for row in result.timeline.timeline
        }
        speed_distribution = {
            f"{result.replay.speed_multiplier}x": result.replay.score,
            "مدعوم": 100.0,
        }
        return {
            "summary": {
                "observation_count": len(result.observations),
                "replay_state": result.state.state,
                "replay_score": result.replay.score,
                "timeline_score": result.timeline.score,
                "quality_score": result.quality.score,
                "readiness_score": result.readiness.score,
                "validation_score": result.validation.score,
                "coverage_score": result.timeline.coverage,
                "warning_count": len(result.diagnostics),
                "recommendation_count": len(result.recommendations),
                "speed_multiplier": result.replay.speed_multiplier,
                "research_only": True,
                "observation_only": True,
                "live_observation_replay": True,
            },
            "replay_quality": result.quality.to_dict(),
            "replay_readiness": result.readiness.to_dict(),
            "replay_coverage": {
                "التغطية": result.timeline.coverage,
                "التسلسل": result.validation.sequence_integrity,
                "الاكتمال": result.validation.observation_completeness,
            },
            "replay_validation": result.validation.to_dict(),
            "replay_stability": {
                "الاستقرار": result.quality.stability,
                "الاعتمادية": result.quality.reliability,
                "الاتساق": result.quality.consistency,
            },
            "source_distribution": dict(source_distribution),
            "timeline_activity": timeline_activity,
            "speed_distribution": speed_distribution,
            "diagnostics_distribution": dict(diagnostics),
            "recommendation_distribution": dict(recommendations),
            "latest": result.to_dict(),
        }
