"""Incident response traceability builder."""

from app.governance_traceability.models import IncidentControlMapping, mapping_item


class IncidentMappingBuilder:
    """Map incident response design to escalation controls."""

    def build(self) -> dict[str, object]:
        areas = [
            "incident severity",
            "escalation path",
            "incident commander",
            "communication requirements",
            "evidence preservation",
            "post-incident review",
        ]
        items = [
            mapping_item(
                index,
                area,
                "incident escalation control",
                "incident",
                "Incident Commander",
                ["incident evidence", "review evidence", "audit evidence"],
            )
            for index, area in enumerate(areas, 1)
        ]
        return IncidentControlMapping(items=items).to_dict()
