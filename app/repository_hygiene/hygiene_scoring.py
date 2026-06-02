"""Repository hygiene scoring."""

from __future__ import annotations

from typing import Any

from app.repository_hygiene.models import HygieneScorecard
from app.repository_hygiene.schemas import HYGIENE_ONLY_FLAGS


class HygieneScoringEngine:
    """Calculate deterministic repository hygiene scores."""

    def build(
        self,
        git_status: dict[str, Any],
        classifications: dict[str, Any],
        retention_policy: dict[str, Any],
        cleanup_plan: dict[str, Any],
        ignore_recommendations: dict[str, Any],
    ) -> dict[str, Any]:
        status_summary = git_status.get("summary", {})
        changed = sum(
            int(status_summary.get(key, 0))
            for key in ("untracked", "modified", "deleted")
        )
        git_score = max(0.0, 100.0 - min(100.0, changed * 4.0))
        classified = len(classifications.get("items", []))
        unknown = sum(
            1
            for item in classifications.get("items", [])
            if item.get("classification") == "unknown"
        )
        classification_score = 100.0 if not classified else max(0.0, 100.0 - unknown)
        retention_score = 100.0 if retention_policy.get("items") else 0.0
        cleanup_score = 100.0 if cleanup_plan.get("items") else 0.0
        ignore_score = 90.0 if ignore_recommendations.get("items") else 100.0
        overall = round(
            (git_score * 0.25)
            + (classification_score * 0.25)
            + (retention_score * 0.2)
            + (cleanup_score * 0.2)
            + (ignore_score * 0.1),
            2,
        )
        return {
            **HygieneScorecard(
                git_status_cleanliness_score=round(git_score, 2),
                artifact_classification_score=round(classification_score, 2),
                retention_policy_coverage_score=round(retention_score, 2),
                cleanup_plan_completeness_score=round(cleanup_score, 2),
                ignore_recommendation_score=round(ignore_score, 2),
                overall_repository_hygiene_score=overall,
                score_status=self.status(overall),
            ).to_dict(),
            **HYGIENE_ONLY_FLAGS,
        }

    def status(self, score: float) -> str:
        if score >= 90:
            return "ممتاز"
        if score >= 80:
            return "جيد"
        if score >= 65:
            return "مقبول"
        if score >= 45:
            return "يحتاج تحسين"
        return "غير جاهز"
