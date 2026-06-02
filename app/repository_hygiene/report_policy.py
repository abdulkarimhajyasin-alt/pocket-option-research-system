"""Report retention policy for repository hygiene."""

from __future__ import annotations

from typing import Any

from app.repository_hygiene.schemas import HYGIENE_ONLY_FLAGS


class ReportPolicyEngine:
    """Build report artifact policy guidance."""

    def build(self) -> dict[str, Any]:
        return {
            "items": [
                {
                    "artifact_type": "release reports",
                    "policy": "retain as release evidence",
                    "manual_review_required": True,
                },
                {
                    "artifact_type": "diagnostics reports",
                    "policy": "retain latest accepted validation evidence",
                    "manual_review_required": True,
                },
            ],
            **HYGIENE_ONLY_FLAGS,
        }
