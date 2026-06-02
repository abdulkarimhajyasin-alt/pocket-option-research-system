"""Baseline decision matrix generation."""

from __future__ import annotations

from typing import Any

from app.release_baseline.models import BaselineDecisionMatrixItem
from app.release_baseline.schemas import BASELINE_ONLY_FLAGS


class BaselineDecisionMatrixEngine:
    """Build human-readable baseline decision matrix."""

    CATEGORIES = (
        (
            "current phase source",
            "آمن",
            "commit",
            "commit recommended",
            "do not touch",
            "none",
            "high",
        ),
        (
            "generated current phase outputs",
            "يحتاج مراجعة",
            "commit after review",
            "commit after review",
            "do not touch",
            "none",
            "medium",
        ),
        (
            "validation churn",
            "يحتاج مراجعة",
            "review",
            "manual decision required",
            "manual cleanup candidate",
            "requires human decision",
            "medium",
        ),
        (
            "archive artifacts",
            "حساس",
            "review",
            "manual decision required",
            "manual cleanup candidate",
            "requires human decision",
            "high",
        ),
        (
            "prompt files",
            "يحتاج مراجعة",
            "commit after review",
            "commit after review",
            "do not touch",
            "none",
            "medium",
        ),
    )

    def build(self) -> dict[str, Any]:
        return {
            "items": [
                BaselineDecisionMatrixItem(
                    file_category=category,
                    risk=risk,
                    recommended_handling=handling,
                    commit_recommendation=commit,
                    cleanup_recommendation=cleanup,
                    ignore_recommendation=ignore,
                    evidence_value=evidence,
                ).to_dict()
                for category, risk, handling, commit, cleanup, ignore, evidence in self.CATEGORIES
            ],
            **BASELINE_ONLY_FLAGS,
        }
