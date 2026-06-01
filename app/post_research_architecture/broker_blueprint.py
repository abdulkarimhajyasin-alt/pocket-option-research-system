"""Architecture-only future broker isolation blueprint."""

from __future__ import annotations

from app.post_research_architecture.models import FutureBrokerIntegrationBlueprint


class BrokerBlueprintBuilder:
    """Build a documents-only broker boundary blueprint."""

    def build(self) -> FutureBrokerIntegrationBlueprint:
        return FutureBrokerIntegrationBlueprint(
            adapter_boundary=[
                "Future broker code must live outside the research platform.",
                "Broker adapters must expose documented contracts only.",
                "Research outputs must not directly call broker interfaces.",
            ],
            broker_isolation_rules=[
                "No broker session state in research modules",
                "No broker network calls from dashboard routes",
                "No broker control from local research scripts",
            ],
            credential_safety_requirements=[
                "Credential vault design required before implementation",
                "No credentials in source, configs, reports, or logs",
                "Credential access must be audited and revocable",
            ],
            session_safety_requirements=[
                "Session lifecycle must be isolated from research services",
                "Session failures must fail closed",
                "Session telemetry must avoid sensitive data",
            ],
            prohibited_current_actions=[
                "Do not add login flows",
                "Do not read account balances",
                "Do not monitor real accounts",
                "Do not modify account state",
            ],
            required_preconditions=[
                "Architecture separation decision",
                "Legal and compliance review",
                "Credential governance approval",
                "Human approval workflow",
            ],
        )
