"""Database strategy design blueprint."""

from app.production_system_design.models import DatabasePlan, design_category


class DatabaseStrategyBuilder:
    """Build database strategy design only."""

    def build(self) -> DatabasePlan:
        return design_category(
            DatabasePlan,
            "database_strategy",
            "Database Strategy",
            [
                "Research artifact storage",
                "Operational event storage",
                "Audit log storage",
                "Configuration history storage",
                "Incident record storage",
                "Immutable ledger concept",
                "Backup and recovery requirements",
            ],
        )
