"""Incident escalation chain builder."""

from app.operational_governance.models import IncidentEscalationPlan, governance_category


class IncidentEscalationBuilder:
    """Build incident escalation governance."""

    def build(self) -> IncidentEscalationPlan:
        return governance_category(
            IncidentEscalationPlan,
            "incident_escalation",
            "Incident Escalation Chains",
            [
                "Incident severity levels",
                "Escalation paths",
                "Operator action boundaries",
                "Incident commander duties",
                "Communication requirements",
                "Evidence preservation",
                "Post-incident review",
            ],
        )
