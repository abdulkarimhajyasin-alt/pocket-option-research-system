"""Service boundary design blueprint."""

from app.production_system_design.models import ServiceBoundary, design_category


class ServiceBoundaryBuilder:
    """Build service boundary design only."""

    def build(self) -> ServiceBoundary:
        return design_category(
            ServiceBoundary,
            "service_boundaries",
            "Service Boundaries",
            [
                "Signal service boundary",
                "Decision review boundary",
                "Risk governance boundary",
                "Execution gateway boundary",
                "Broker isolation boundary",
                "Monitoring boundary",
                "Audit trail boundary",
                "Operations boundary",
            ],
        )
