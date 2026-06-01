"""Architecture domains for the future program foundation."""

from __future__ import annotations

from app.trading_architecture_program.models import ArchitectureDomain


class ArchitectureDomainBuilder:
    """Build architecture-only future program domains."""

    def build(self) -> list[ArchitectureDomain]:
        domains = [
            ("execution", "Execution Domain", "Future execution architecture boundaries."),
            ("broker", "Broker Domain", "Future broker isolation architecture."),
            ("risk", "Risk Domain", "Future risk governance architecture."),
            (
                "monitoring",
                "Monitoring Domain",
                "Future monitoring and observability architecture.",
            ),
            ("governance", "Governance Domain", "Future approval and control architecture."),
            ("compliance", "Compliance Domain", "Future legal and regulatory review architecture."),
            (
                "infrastructure",
                "Infrastructure Domain",
                "Future platform infrastructure architecture.",
            ),
            ("operations", "Operations Domain", "Future operational readiness architecture."),
        ]
        prohibited = [
            "real trade execution",
            "broker connectivity",
            "credential handling",
            "order placement",
            "live trading",
            "money handling",
        ]
        return [
            ArchitectureDomain(
                domain_id=domain_id,
                name=name,
                purpose=purpose,
                prohibited_capabilities=prohibited,
            )
            for domain_id, name, purpose in domains
        ]
