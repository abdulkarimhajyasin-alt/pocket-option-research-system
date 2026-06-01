"""Change management control builder."""

from app.operational_governance.models import ChangeControl, governance_category


class ChangeManagementBuilder:
    """Build change management controls."""

    def build(self) -> ChangeControl:
        return governance_category(
            ChangeControl,
            "change_management",
            "Change Management Controls",
            [
                "Change request model",
                "Impact assessment",
                "Risk assessment",
                "Approval requirements",
                "Rollback plan requirement",
                "Evidence requirement",
                "Post-change review",
            ],
        )
