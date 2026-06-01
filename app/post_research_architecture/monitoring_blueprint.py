"""Architecture-only future monitoring blueprint."""

from __future__ import annotations

from app.post_research_architecture.models import FutureMonitoringArchitectureBlueprint


class MonitoringBlueprintBuilder:
    """Build a documents-only operational monitoring blueprint."""

    def build(self) -> FutureMonitoringArchitectureBlueprint:
        return FutureMonitoringArchitectureBlueprint(
            monitoring_domains=[
                "System health",
                "Data freshness",
                "Risk service availability",
                "Command queue state",
                "External dependency status",
                "Human approval latency",
            ],
            health_checks=[
                "Heartbeat",
                "Data lag",
                "Report freshness",
                "Queue depth",
                "Error-rate threshold",
            ],
            alerting_requirements=[
                "Severity levels",
                "Escalation owner",
                "Acknowledgement tracking",
                "False-positive review",
            ],
            observability_requirements=[
                "Structured logs",
                "Metrics snapshots",
                "Traceable request ids",
                "Dashboard health views",
            ],
            logs=[
                "Architecture events",
                "Risk decisions",
                "Approval events",
                "Incident events",
            ],
            metrics=[
                "Latency",
                "Freshness",
                "Error rate",
                "Rejection count",
                "Disable events",
            ],
            incident_review=[
                "Root-cause review",
                "Timeline reconstruction",
                "Control effectiveness assessment",
                "Action item tracking",
            ],
        )
