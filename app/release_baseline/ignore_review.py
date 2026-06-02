"""Ignore rule review proposal."""

from __future__ import annotations

from typing import Any

from app.release_baseline.models import IgnoreReviewItem
from app.release_baseline.schemas import BASELINE_ONLY_FLAGS


class IgnoreReviewEngine:
    """Build .gitignore review proposal without editing .gitignore."""

    def build(self, sources: dict[str, Any]) -> dict[str, Any]:
        hygiene_files = sources.get("sources", {}).get("repository_hygiene", {}).get("files", [])
        recommendations = []
        for item in hygiene_files:
            if item.get("name") == "ignore_recommendations.json":
                payload = item.get("payload", {})
                recommendations.extend(
                    payload.get("items", []) if isinstance(payload, dict) else []
                )
        rows = [
            IgnoreReviewItem(
                pattern=str(item.get("pattern", "")),
                confidence=self._confidence(str(item.get("confidence", ""))),
                reason=str(item.get("reason", "")),
                review_only=True,
            ).to_dict()
            for item in recommendations
        ]
        return {"items": rows, **BASELINE_ONLY_FLAGS}

    def _confidence(self, value: str) -> str:
        if value in {"مرتفع", "high confidence"}:
            return "high confidence"
        if value in {"منخفض", "low confidence"}:
            return "low confidence"
        if not value:
            return "requires human decision"
        return "medium confidence"
