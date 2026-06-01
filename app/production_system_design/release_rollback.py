"""Release and rollback design blueprint."""

from app.production_system_design.models import ReleaseRollbackPlan, design_category


class ReleaseRollbackBuilder:
    """Build release and rollback design only."""

    def build(self) -> ReleaseRollbackPlan:
        return design_category(
            ReleaseRollbackPlan,
            "release_rollback",
            "Release and Rollback Design",
            [
                "Release gates",
                "Deployment approval",
                "Canary concept",
                "Rollback triggers",
                "Version freeze",
                "Post-release monitoring",
                "Emergency rollback",
            ],
        )
