"""Operator responsibility model builder."""

from app.operational_governance.models import OperatorResponsibility, governance_category


class OperatorResponsibilityBuilder:
    """Build operator responsibility model."""

    def build(self) -> OperatorResponsibility:
        return governance_category(
            OperatorResponsibility,
            "operator_responsibility",
            "Operator Responsibility Model",
            [
                "Operator responsibilities",
                "Prohibited operator actions",
                "Required reviews",
                "Shift handoff concept",
                "Incident duties",
                "Escalation duties",
                "Documentation duties",
            ],
        )
