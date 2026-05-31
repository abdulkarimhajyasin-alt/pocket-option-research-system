"""Visibility assessment for read-only browser observation artifacts."""

from __future__ import annotations

from app.browser_observation.models import ObservationArtifact
from app.browser_observation.models import ParseResult
from app.browser_observation.models import VisibilityResult
from app.browser_observation.validator import average
from app.browser_observation.validator import clamp


class VisibilityAssessmentEngine:
    """Evaluate observable coverage, field completeness, and report visibility."""

    def assess(
        self,
        artifacts: tuple[ObservationArtifact, ...],
        parse: ParseResult,
    ) -> VisibilityResult:
        count = len(artifacts)
        visible = sum(1 for item in artifacts if item.visibility_status == "مرئي")
        valid_fields = sum(
            1
            for value in (
                parse.visible_assets,
                parse.visible_payouts,
                parse.visible_sessions,
                parse.visible_symbols,
                parse.visible_timestamps,
                parse.visible_market_data,
            )
            if value > 0
        )
        observable_coverage = (visible / count * 100.0) if count else 0.0
        field_completeness = valid_fields / 6 * 100.0
        data_visibility = parse.score
        report_visibility = min(100.0, count * 20.0)
        return VisibilityResult(
            score=average(
                [
                    observable_coverage,
                    field_completeness,
                    data_visibility,
                    report_visibility,
                ]
            ),
            observable_coverage=clamp(observable_coverage),
            field_completeness=clamp(field_completeness),
            data_visibility=clamp(data_visibility),
            report_visibility=clamp(report_visibility),
        )
