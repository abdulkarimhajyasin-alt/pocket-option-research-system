"""Emergency stop governance builder."""

from app.operational_governance.models import KillSwitchGovernancePlan, governance_category


class KillSwitchGovernanceBuilder:
    """Build emergency stop governance without any active control."""

    def build(self) -> KillSwitchGovernancePlan:
        return governance_category(
            KillSwitchGovernancePlan,
            "kill_switch_governance",
            "Emergency Stop Governance",
            [
                "Emergency stop ownership",
                "Activation criteria",
                "Activation authority",
                "Manual approval requirements",
                "Emergency stop procedure",
                "Evidence requirements",
                "Recovery procedure",
            ],
        )
