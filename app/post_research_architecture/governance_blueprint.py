"""Architecture-only future governance blueprint."""

from __future__ import annotations

from app.post_research_architecture.models import FutureGovernanceBlueprint


class GovernanceBlueprintBuilder:
    """Build a documents-only governance blueprint."""

    def build(self) -> FutureGovernanceBlueprint:
        return FutureGovernanceBlueprint(
            approval_gates=[
                "Research freeze approval",
                "Architecture separation approval",
                "Risk design approval",
                "Compliance approval",
                "External feasibility approval",
            ],
            human_review_requirements=[
                "Human review for every program-stage transition",
                "Human approval for any future external integration design",
                "Human signoff before feasibility testing",
            ],
            audit_trails=[
                "Decision records",
                "Approval records",
                "Risk review records",
                "Release records",
            ],
            change_control=[
                "No unreviewed architectural changes",
                "Separate change requests for future-system work",
                "Rollback plan required before implementation approval",
            ],
            release_control=[
                "Research platform releases remain separate",
                "Future program releases require independent certification",
                "No mixed research and future-system release train",
            ],
            safety_reviews=[
                "Boundary review",
                "Forbidden capability review",
                "Incident readiness review",
                "Compliance review",
            ],
            rollback_policy=[
                "Revert future-program changes independently",
                "Preserve research release artifacts",
                "Fail closed on unresolved safety issues",
            ],
        )
