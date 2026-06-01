"""Logging strategy design blueprint."""

from app.production_system_design.models import LoggingPlan, design_category


class LoggingStrategyBuilder:
    """Build logging strategy design only."""

    def build(self) -> LoggingPlan:
        return design_category(
            LoggingPlan,
            "logging_strategy",
            "Logging Strategy",
            [
                "Structured logs",
                "Correlation IDs",
                "Trace IDs",
                "Audit logs",
                "Safety logs",
                "Incident logs",
                "Retention requirements",
            ],
        )
