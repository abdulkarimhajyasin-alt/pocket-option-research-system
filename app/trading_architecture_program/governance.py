"""Governance foundations for the architecture program."""

from __future__ import annotations


class ProgramGovernanceBuilder:
    """Build program governance metadata."""

    def build(self) -> dict[str, object]:
        return {
            "approval_model": "human-review-required",
            "change_control": "separate-program-change-control",
            "release_control": "architecture-artifacts-only",
            "live_trading_approval": False,
            "required_reviews": [
                "architecture review",
                "risk review",
                "governance review",
                "compliance review",
            ],
            "architecture_only": True,
            "research_only": True,
        }
