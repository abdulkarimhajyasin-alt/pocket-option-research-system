"""Alerting strategy design blueprint."""

from app.production_system_design.models import AlertingPlan, design_category


class AlertingStrategyBuilder:
    """Build alerting strategy design only."""

    def build(self) -> AlertingPlan:
        return design_category(
            AlertingPlan,
            "alerting_strategy",
            "Alerting Strategy",
            [
                "Alert severity",
                "Alert routing",
                "Emergency alerts",
                "False positive management",
                "Escalation policy",
                "Alert acknowledgement",
            ],
        )
