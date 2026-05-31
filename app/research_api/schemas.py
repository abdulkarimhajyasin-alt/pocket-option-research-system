"""Stable schema helpers for unified research API payloads."""

from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "research_api.v1"

VIEW_KEYS = (
    "view_id",
    "label_ar",
    "data",
    "available",
    "metadata",
)

SNAPSHOT_KEYS = (
    "snapshot_id",
    "generated_at",
    "signals",
    "opportunities",
    "paper",
    "readiness",
    "knowledge_graph",
    "diagnostics",
    "recommendations",
    "labels_ar",
    "metadata",
    "research_only",
    "local_only",
    "not_execution",
    "not_broker_access",
    "not_browser_automation",
)


def schema_metadata() -> dict[str, Any]:
    """Return stable schema metadata."""
    return {
        "schema_version": SCHEMA_VERSION,
        "snapshot_keys": list(SNAPSHOT_KEYS),
        "view_keys": list(VIEW_KEYS),
        "stable_json_schema": True,
    }
