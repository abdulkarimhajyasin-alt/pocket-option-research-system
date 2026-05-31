"""Stable schemas for research archive outputs."""

SCHEMA_VERSION = "research_archive.v1"
VERSION_PREFIX = "research-v"

SNAPSHOT_KEYS = (
    "snapshot_id",
    "version",
    "created_at",
    "source_summary",
    "included_sources",
    "missing_sources",
    "checksum",
    "safety_status",
    "research_only",
    "schema_version",
)

VERSION_KEYS = (
    "version_id",
    "version_label",
    "snapshot_id",
    "created_at",
    "previous_version_id",
    "checksum",
    "metadata",
    "safety_boundary",
)


def schema_metadata() -> dict[str, object]:
    """Return archive schema metadata."""
    return {
        "schema_version": SCHEMA_VERSION,
        "stable_json_schema": True,
        "research_archive_only": True,
    }
