"""Incident response design blueprint."""

from app.production_system_design.models import IncidentResponsePlan, design_category


class IncidentResponseBuilder:
    """Build incident response design only."""

    def build(self) -> IncidentResponsePlan:
        return design_category(
            IncidentResponsePlan,
            "incident_response",
            "Incident Response Design",
            [
                "Incident categories",
                "Stop conditions",
                "Operator actions",
                "Escalation",
                "Rollback",
                "Post-incident review",
                "Evidence preservation",
            ],
        )
