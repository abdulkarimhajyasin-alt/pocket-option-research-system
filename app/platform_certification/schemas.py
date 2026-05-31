"""Schemas and constants for final platform certification."""

SCHEMA_VERSION = "platform_certification.v1"

CERTIFICATION_STATES = (
    "Not Certified",
    "Conditionally Certified",
    "Certified For Advanced Research",
)

FORBIDDEN_STATES = (
    "Approved For Live Trading",
    "Approved For Execution",
    "Broker Ready",
)

DOMAIN_NAMES = (
    "architecture",
    "safety",
    "research_quality",
    "knowledge_graph",
    "research_api",
    "research_archive",
    "dashboard",
    "observation",
    "paper_trading",
    "readiness",
)
