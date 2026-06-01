"""Monitoring strategy design blueprint."""

from app.production_system_design.models import MonitoringPlan, design_category


class MonitoringStrategyBuilder:
    """Build monitoring strategy design only."""

    def build(self) -> MonitoringPlan:
        return design_category(
            MonitoringPlan,
            "monitoring_strategy",
            "Monitoring Strategy",
            [
                "Service health",
                "Risk health",
                "Execution safety health",
                "Broker isolation health",
                "Data freshness",
                "Queue health",
                "Operator alerts",
                "Dashboard health",
            ],
        )
