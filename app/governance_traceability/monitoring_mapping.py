"""Monitoring and alerting traceability builder."""

from app.governance_traceability.models import MonitoringControlMapping, mapping_item


class MonitoringMappingBuilder:
    """Map monitoring and alerting design to operator controls."""

    def build(self) -> dict[str, object]:
        areas = [
            "service health monitoring",
            "risk health monitoring",
            "data freshness monitoring",
            "alert acknowledgement",
            "operator escalation",
            "monitoring audit trail",
        ]
        items = [
            mapping_item(
                index,
                area,
                "operator monitoring control",
                "monitoring",
                "Operations Lead",
                ["monitoring evidence", "audit evidence", "escalation evidence"],
            )
            for index, area in enumerate(areas, 1)
        ]
        return MonitoringControlMapping(items=items).to_dict()
