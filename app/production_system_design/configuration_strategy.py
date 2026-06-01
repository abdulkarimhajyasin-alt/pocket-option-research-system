"""Configuration strategy design blueprint."""

from app.production_system_design.models import ConfigurationPlan, design_category


class ConfigurationStrategyBuilder:
    """Build configuration strategy design only."""

    def build(self) -> ConfigurationPlan:
        return design_category(
            ConfigurationPlan,
            "configuration_strategy",
            "Configuration Strategy",
            [
                "Typed configuration requirements",
                "Environment-specific configs",
                "Immutable runtime settings",
                "Change approval requirements",
                "Config validation requirements",
                "Rollbackable configuration",
            ],
        )
