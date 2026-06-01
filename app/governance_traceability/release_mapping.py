"""Release and rollback traceability builder."""

from app.governance_traceability.models import ReleaseControlMapping, mapping_item


class ReleaseMappingBuilder:
    """Map release and rollback design to governance approvals."""

    def build(self) -> dict[str, object]:
        areas = [
            "release candidate review",
            "release gate checklist",
            "rollback approval",
            "rollback evidence",
            "release freeze",
            "post-release review",
        ]
        items = [
            mapping_item(
                index,
                area,
                "release governance control",
                "release",
                "Release Review Board",
                ["approval evidence", "rollback evidence", "review evidence"],
            )
            for index, area in enumerate(areas, 1)
        ]
        return ReleaseControlMapping(items=items).to_dict()
