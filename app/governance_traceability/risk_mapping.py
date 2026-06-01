"""Risk-to-control mapping builder."""

from app.governance_traceability.models import RiskControlMapping, mapping_item


class RiskMappingBuilder:
    """Map risk-sensitive areas to governance controls."""

    def build(self) -> dict[str, object]:
        areas = [
            "risk policy changes",
            "secrets strategy",
            "configuration strategy",
            "execution safety boundary",
            "broker isolation boundary",
            "monitoring failure",
            "release rollback risk",
        ]
        items = [
            mapping_item(
                index,
                area,
                "risk governance control",
                "risk",
                "Risk Owner",
                ["risk evidence", "audit evidence", "mitigation evidence"],
            )
            for index, area in enumerate(areas, 1)
        ]
        return RiskControlMapping(items=items).to_dict()
