"""Production topology design blueprint."""

from app.production_system_design.models import ProductionTopology, design_category


class ProductionTopologyBuilder:
    """Build future production topology design only."""

    def build(self) -> ProductionTopology:
        return design_category(
            ProductionTopology,
            "topology",
            "Production Topology",
            [
                "Research system boundary",
                "Trading architecture program boundary",
                "Future production boundary",
                "Operator boundary",
                "Audit boundary",
                "Monitoring boundary",
                "Data boundary",
            ],
        )
