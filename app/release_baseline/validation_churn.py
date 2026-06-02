"""Validation churn analysis."""

from __future__ import annotations

from typing import Any

from app.release_baseline.models import ValidationChurnItem, count_by
from app.release_baseline.schemas import BASELINE_ONLY_FLAGS


class ValidationChurnAnalysisEngine:
    """Analyze files likely modified by validation runs."""

    def analyze(self, sources: dict[str, Any]) -> dict[str, Any]:
        rows = []
        for item in sources.get("git_status", {}).get("items", []):
            path = str(item.get("path", ""))
            category = str(item.get("category", ""))
            if category in {"generated report change", "generated storage change"}:
                churn_type = self._type(path)
                rows.append(
                    ValidationChurnItem(
                        path=path,
                        churn_type=churn_type,
                        reason="Generated report/storage file changed during validation.",
                    ).to_dict()
                )
        return {"items": rows, "churn_counts": count_by(rows, "churn_type"), **BASELINE_ONLY_FLAGS}

    def _type(self, path: str) -> str:
        if "release_packaging" in path or "certification" in path:
            return "release evidence churn"
        if "research_archive" in path:
            return "manual review required"
        if "diagnostics" in path:
            return "expected validation churn"
        return "validation churn"
