"""Archive retention policy for repository hygiene."""

from __future__ import annotations

from typing import Any

from app.repository_hygiene.models import ArchiveRetentionRule
from app.repository_hygiene.schemas import HYGIENE_ONLY_FLAGS


class ArchivePolicyEngine:
    """Build archive-specific policy guidance."""

    def build(self) -> dict[str, Any]:
        return {
            "rule": ArchiveRetentionRule().to_dict(),
            "notes": [
                "Preserve release evidence snapshots.",
                "Review older snapshots manually before any cleanup.",
                "Do not delete archive files automatically.",
            ],
            **HYGIENE_ONLY_FLAGS,
        }
