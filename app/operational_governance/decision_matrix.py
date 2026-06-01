"""Decision authority matrix builder."""

from app.operational_governance.models import DecisionAuthorityRule, governance_category


class DecisionMatrixBuilder:
    """Build decision authority rules without direct trading approval."""

    def build(self) -> DecisionAuthorityRule:
        return governance_category(
            DecisionAuthorityRule,
            "decision_matrix",
            "Decision Authority Matrix",
            [
                "Architecture change authority",
                "Risk change authority",
                "Monitoring change authority",
                "Production design change authority",
                "Release movement authority",
                "Incident closure authority",
                "Emergency recovery authority",
                "External feasibility study authority",
            ],
        )
