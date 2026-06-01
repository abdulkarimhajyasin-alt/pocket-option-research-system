"""Release governance builder."""

from app.operational_governance.models import ReleaseGovernancePlan, governance_category


class ReleaseGovernanceBuilder:
    """Build release governance plan without deployment behavior."""

    def build(self) -> ReleaseGovernancePlan:
        return governance_category(
            ReleaseGovernancePlan,
            "release_governance",
            "Release Governance",
            [
                "Release candidate review",
                "Release gate checklist",
                "Safety review",
                "Risk review",
                "Monitoring readiness review",
                "Rollback readiness review",
                "Release freeze",
                "Post-release review",
            ],
        )
