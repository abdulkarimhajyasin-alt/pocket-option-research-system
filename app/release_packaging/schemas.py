"""Schemas and constants for release packaging."""

SCHEMA_VERSION = "release_packaging.v1"
RELEASE_ID = "research-platform-v1.0"
RELEASE_LABEL = "Research Platform v1.0"
RELEASE_VERSION = "v1.0"
CREATED_AT = "deterministic-research-platform-v1-release"

SAFE_RELEASE_STATUSES = (
    "Ready For Research Release",
    "Ready With Warnings",
    "Not Ready",
)

FORBIDDEN_RELEASE_STATUSES = (
    "Ready For Live Trading",
    "Broker Ready",
    "Execution Ready",
)

COMPLETED_PHASES = tuple(range(1, 56))
PHASE_RANGE = "1-55"
