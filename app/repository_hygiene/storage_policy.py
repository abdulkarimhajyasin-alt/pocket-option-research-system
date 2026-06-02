"""Storage retention policy for repository hygiene."""

from __future__ import annotations

from typing import Any

from app.repository_hygiene.schemas import HYGIENE_ONLY_FLAGS


class StoragePolicyEngine:
    """Build storage artifact policy guidance."""

    def build(self) -> dict[str, Any]:
        return {
            "items": [
                {
                    "artifact_type": "storage summaries",
                    "policy": "retain when referenced by reports or dashboards",
                    "manual_review_required": True,
                },
                {
                    "artifact_type": "temporary generated storage",
                    "policy": "manual cleanup planning only",
                    "manual_review_required": True,
                },
            ],
            **HYGIENE_ONLY_FLAGS,
        }
